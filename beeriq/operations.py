"""Deterministic, audit-friendly event-driven beer + empties automation demo.
All data, SAP records, and fleet assignments in this module are SIMULATED.
"""
from __future__ import annotations
from copy import deepcopy
from datetime import datetime, timezone
from math import ceil

CATALOG = {
    'Lager 24-pack': {'stock': 110, 'demand_per_day': 40, 'unit_cost_cad': 34, 'warehouse': 1300},
    'Pilsner 12-pack': {'stock': 165, 'demand_per_day': 22, 'unit_cost_cad': 21, 'warehouse': 980},
    'Craft Pale Ale 6-pack': {'stock': 48, 'demand_per_day': 13, 'unit_cost_cad': 17, 'warehouse': 410},
    'Non-alcoholic 6-pack': {'stock': 76, 'demand_per_day': 8, 'unit_cost_cad': 14, 'warehouse': 380},
}
RETURN_TYPES = {'Refillable glass': 180, 'Metal cans': 320, 'Non-refillable glass': 90}
STORES = ('Toronto Demo 01', 'Mississauga Demo 02', 'Brampton Demo 03')

def init_demo(store='Toronto Demo 01'):
    if store not in STORES: raise ValueError('Unknown synthetic store')
    return {'store': store, 'inventory': {k:v['stock'] for k,v in CATALOG.items()},
            'warehouse': {k:v['warehouse'] for k,v in CATALOG.items()},
            'return_balances': dict(RETURN_TYPES), 'empty_capacity': 1200,
            'orders': [], 'pickups': [], 'events': [], 'exceptions': [],
            'truck_assignments': [], 'event_ids': set(), 'seq': 0,
            'received_units': 0, 'sold_units': 0, 'returned_containers': 0,
            'manual_actions_avoided': 0}

def emit(state, kind, detail):
    state['seq'] += 1
    row={'step':state['seq'], 'event':kind, 'detail':detail, 'demo_time':f'09:{state["seq"]%60:02d}'}
    state['events'].append(row)
    return row

def inventory_position(state, sku):
    open_orders=sum(o['quantity'] for o in state['orders'] if o['sku']==sku and o['status'] in ('ERP accepted','Awaiting approval','Warehouse allocated','Dispatched'))
    return state['inventory'][sku] + open_orders

def reorder_point(sku, lead_days=3, safety_days=1):
    return CATALOG[sku]['demand_per_day']*(lead_days+safety_days)

def _create_order(state, sku):
    if inventory_position(state, sku) >= reorder_point(sku):
        return None
    # 7-day target position; rounded to a whole carton multiple of 6.
    target=CATALOG[sku]['demand_per_day']*7
    quantity=ceil(max(0,target-inventory_position(state,sku))/6)*6
    if not quantity: return None
    high_value=(quantity*CATALOG[sku]['unit_cost_cad'])>4000
    order={'id':f'SAP-DEMO-{len(state["orders"])+1:04d}','sku':sku,'quantity':quantity,
           'status':'Awaiting approval' if high_value else 'ERP accepted',
           'value_cad':quantity*CATALOG[sku]['unit_cost_cad'],
           'reason':f'Inventory position below reorder point {reorder_point(sku)}; 7-day target; multiple of 6',
           'store':state['store']}
    state['orders'].append(order)
    emit(state,'ERP replenishment request',f'{order["id"]} · {sku} · {quantity} units · {order["status"]}')
    if high_value:
        state['exceptions'].append({'type':'Approval required','item':order['id'],'reason':'Order value exceeds CAD 4,000','status':'Open'})
    else:
        state['manual_actions_avoided']+=1
        _allocate(state, order)
    return order

def _allocate(state,order):
    if order['status'] != 'ERP accepted':return
    if state['warehouse'][order['sku']] < order['quantity']:
        order['status']='Warehouse shortfall'
        state['exceptions'].append({'type':'Warehouse shortfall','item':order['id'],'reason':'Available demo warehouse stock is insufficient','status':'Open'})
        emit(state,'Warehouse exception',order['id']+' awaiting stock')
        return
    state['warehouse'][order['sku']]-=order['quantity']
    order['status']='Warehouse allocated'
    emit(state,'Warehouse allocation',f'{order["id"]} · {order["quantity"]} units reserved')
    truck_id=f'TRUCK-DEMO-{(len(state["truck_assignments"])%3)+1:02d}'
    order['truck']=truck_id
    order['status']='Dispatched'
    state['truck_assignments'].append({'truck':truck_id,'activity':'Full-case delivery','reference':order['id'],'store':state['store'],'load':order['quantity'],'status':'Scheduled (simulation)'})
    emit(state,'Delivery scheduled',f'{truck_id} assigned to {order["id"]}')
    state['manual_actions_avoided']+=2 # warehouse handoff & scheduling

def record_sale(state, sku, quantity, event_id):
    if event_id in state['event_ids']: return False
    if sku not in CATALOG or not isinstance(quantity,int) or quantity<=0:raise ValueError('Invalid SKU or sale quantity')
    state['event_ids'].add(event_id)
    state['inventory'][sku]-=quantity
    state['sold_units']+=quantity
    emit(state,'POS transaction',f'{quantity} × {sku}; stock now {state["inventory"][sku]}')
    if state['inventory'][sku]<0:
        state['exceptions'].append({'type':'Inventory exception','item':sku,'reason':'Negative expected stock; verify POS / inventory','status':'Open'})
    _create_order(state,sku)
    return True

def record_return(state, container_type, quantity, event_id):
    if event_id in state['event_ids']:return False
    if container_type not in RETURN_TYPES or not isinstance(quantity,int) or quantity<=0:raise ValueError('Invalid return transaction')
    state['event_ids'].add(event_id)
    state['return_balances'][container_type]+=quantity
    state['returned_containers']+=quantity
    emit(state,'Empty-container return',f'{quantity} × {container_type} logged from return/POS event')
    if sum(state['return_balances'].values())>=.8*state['empty_capacity']:
        pending=sum(p['quantity'] for p in state['pickups'] if p['status'] in ('Pickup scheduled','Awaiting confirmation'))
        if pending==0:
            pickup={'id':f'EMPTY-DEMO-{len(state["pickups"])+1:04d}',
                    'quantity':sum(state['return_balances'].values()),'status':'Pickup scheduled',
                    'store':state['store']}
            state['pickups'].append(pickup)
            truck_id=f'TRUCK-DEMO-{(len(state["truck_assignments"])%3)+1:02d}'
            pickup['truck']=truck_id
            state['truck_assignments'].append({'truck':truck_id,'activity':'Empties collection','reference':pickup['id'],'store':state['store'],'load':pickup['quantity'],'status':'Scheduled (simulation)'})
            emit(state,'Empty pickup created',f'{pickup["id"]}: {pickup["quantity"]} returns, {truck_id} assigned')
            state['manual_actions_avoided']+=2 # pickup request & scheduling
    return True

def approve_order(state, order_id):
    order=next((o for o in state['orders'] if o['id']==order_id),None)
    if not order or order['status']!='Awaiting approval':return False
    order['status']='ERP accepted'
    for e in state['exceptions']:
        if e['item']==order_id and e['type']=='Approval required':e['status']='Resolved'
    emit(state,'Manager approved order',order_id)
    _allocate(state,order)
    return True

def confirm_delivery(state, order_id, received):
    order=next((o for o in state['orders'] if o['id']==order_id),None)
    if not order or order['status']!='Dispatched' or received<0 or received>order['quantity']:return False
    state['inventory'][order['sku']]+=received
    state['received_units']+=received
    order['status']='Received' if received==order['quantity'] else 'Receipt discrepancy'
    emit(state,'Store receipt',f'{order_id}: {received}/{order["quantity"]} units confirmed')
    if received!=order['quantity']:
        state['exceptions'].append({'type':'Receipt discrepancy','item':order_id,'reason':'Received count differs from shipped count','status':'Open'})
    return True

def confirm_empty_pickup(state, pickup_id, confirmed):
    pickup=next((p for p in state['pickups'] if p['id']==pickup_id),None)
    if not pickup or pickup['status']!='Pickup scheduled' or confirmed<0 or confirmed>pickup['quantity']:return False
    # Remove accepted container counts FIFO by type; total balance cannot go negative.
    remaining=confirmed
    for kind in state['return_balances']:
        taken=min(remaining,state['return_balances'][kind])
        state['return_balances'][kind]-=taken
        remaining-=taken
    pickup['status']='Collected' if confirmed==pickup['quantity'] else 'Pickup discrepancy'
    emit(state,'Empty pickup verified',f'{pickup_id}: scanned {confirmed} containers')
    if confirmed!=pickup['quantity']:
        state['exceptions'].append({'type':'Empty pickup discrepancy','item':pickup_id,'reason':'Scanned count differs from expected count','status':'Open'})
    return True

def reconcile_count(state,sku,physical_count):
    if sku not in CATALOG or not isinstance(physical_count,int) or physical_count<0:raise ValueError('Invalid cycle count')
    variance=physical_count-state['inventory'][sku]
    emit(state,'Cycle count checked',f'{sku} · expected {state["inventory"][sku]} · physical {physical_count} · variance {variance:+d}')
    if variance:
        state['exceptions'].append({'type':'Stock variance','item':sku,'reason':f'Variance {variance:+d}; investigate scanning, damage, receiving or shrinkage','status':'Open'})
    return variance

def run_demo_day(state):
    # fixed, repeatable events to make the full automation auditable.
    purchases=[('Lager 24-pack',18),('Pilsner 12-pack',14),('Craft Pale Ale 6-pack',10),('Non-alcoholic 6-pack',6)]
    for idx,(sku,quantity) in enumerate(purchases):record_sale(state,sku,quantity,f'DAY1-POS-{idx}')
    for idx,(kind,quantity) in enumerate([('Metal cans',450),('Refillable glass',210),('Non-refillable glass',90)]):
        record_return(state,kind,quantity,f'DAY1-RETURN-{idx}')
    return state

def state_summary(state):
    return {'Transactions processed':len([e for e in state['events'] if e['event']=='POS transaction']),
            'Units sold':state['sold_units'], 'ERP requests':len(state['orders']),
            'Warehouse / fleet assignments':len(state['truck_assignments']),
            'Empty pickups scheduled':len(state['pickups']),
            'Open exceptions':sum(e['status']=='Open' for e in state['exceptions']),
            'Estimated manual steps avoided':state['manual_actions_avoided']}
