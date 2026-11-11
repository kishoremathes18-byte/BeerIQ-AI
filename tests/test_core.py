from pathlib import Path
import pandas as pd
import pytest
from beeriq.core import load_sales,kpis,sales_breakdown,quality_sales,forecast,stock_priorities,plan_pickups,haversine
from beeriq.agent import execute_tool

DATA=Path(__file__).parents[1]/'data'

def sample():
    return load_sales(pd.read_csv(DATA/'synthetic_sales.csv'))

def test_revenue_is_units_times_prices():
    d=sample()
    assert (d.revenue == (d.units*d.unit_price).round(2)).all()
    assert kpis(d)['gross_profit'] == round(float(d.gross_profit.sum()),2)

def test_invalid_schema_rejected():
    with pytest.raises(ValueError): load_sales(pd.DataFrame({'date':['2026-01-01']}))

def test_negative_values_rejected():
    with pytest.raises(ValueError): load_sales(pd.DataFrame([dict(date='2026-01-01',store='A',product='B',units=-1,unit_price=5,unit_cost=2)]))

def test_breakdown_reconciles_to_total():
    d=sample()
    assert abs(float(sales_breakdown(d,'store',50).revenue.sum())-float(d.revenue.sum()))<.01

def test_forecast_returns_nonnegative():
    d=sample()
    result=forecast(d,'Toronto Central','Classic Lager A',7)
    assert result['estimated_units'] >= 0
    assert result['historical_days']==28

def test_quality_join():
    d=sample(); c=pd.read_csv(DATA/'synthetic_catalog.csv')
    assert len(quality_sales(d,c)) == d['product'].nunique()

def test_stock_priorities():
    result=stock_priorities(sample(),pd.read_csv(DATA/'synthetic_inventory.csv'))
    assert len(result)>0 and result.iloc[0].surplus_units <= result.iloc[-1].surplus_units

def test_distance():
    assert haversine(0,0,0,0)==0
    assert haversine(43.7,-79.4,43.6,-79.5)>0

def test_routes_capacity_and_unique_stops():
    plan=plan_pickups(pd.read_csv(DATA/'synthetic_collection_locations.csv'),vehicle_count=5)
    stops=[]
    for route in plan['routes']:
        assert route['load']<=2400
        stops.extend(s['location'] for s in route['stops'])
    assert len(stops)==len(set(stops))
    assert plan['selected_locations']==plan['scheduled_locations']+len(plan['unscheduled'])

def test_agent_dispatch():
    d=sample(); c=pd.read_csv(DATA/'synthetic_catalog.csv'); i=pd.read_csv(DATA/'synthetic_inventory.csv'); l=pd.read_csv(DATA/'synthetic_collection_locations.csv')
    output=execute_tool('get_business_overview',{},d,c,i,l)
    assert output['transactions']==len(d)
    with pytest.raises(ValueError): execute_tool('unrecognized',{},d,c,i,l)
