from beeriq.operations import init_demo,run_demo_day,record_sale,record_return,reconcile_count,confirm_delivery,confirm_empty_pickup,state_summary

def test_sale_and_dedupe():
 s=init_demo(); old=s['inventory']['Lager 24-pack']; assert record_sale(s,'Lager 24-pack',3,'e1'); assert not record_sale(s,'Lager 24-pack',3,'e1'); assert s['inventory']['Lager 24-pack']==old-3

def test_replenishment_is_not_repeated():
 s=init_demo();record_sale(s,'Lager 24-pack',5,'e1');record_sale(s,'Lager 24-pack',2,'e2');assert len(s['orders'])==1

def test_demo_day_and_pickups():
 s=init_demo();run_demo_day(s);assert s['orders'];assert s['pickups'];assert s['truck_assignments'];assert state_summary(s)['Units sold']==48

def test_delivery_count_adds_stock_only_once():
 s=init_demo();run_demo_day(s);o=next(x for x in s['orders'] if x['status']=='Dispatched');old=s['inventory'][o['sku']];assert confirm_delivery(s,o['id'],o['quantity']);assert s['inventory'][o['sku']]==old+o['quantity'];assert not confirm_delivery(s,o['id'],o['quantity'])

def test_empty_pickup_balance():
 s=init_demo();run_demo_day(s);p=s['pickups'][0];before=sum(s['return_balances'].values());assert confirm_empty_pickup(s,p['id'],p['quantity']);assert sum(s['return_balances'].values())==before-p['quantity']

def test_variance_not_theft():
 s=init_demo();assert reconcile_count(s,'Pilsner 12-pack',160)==-5;assert s['exceptions'][-1]['type']=='Stock variance';assert 'investigate' in s['exceptions'][-1]['reason']
