import pandas as pd
from beeriq.free_agent import analyze_question
from beeriq.core import load_sales


def fixtures():
    sales = load_sales(pd.DataFrame([
        {'date':'2026-01-01','store':'A','product':'P','units':5,'unit_price':10,'unit_cost':6},
        {'date':'2026-02-01','store':'A','product':'P','units':8,'unit_price':10,'unit_cost':6},
    ]))
    catalog = pd.DataFrame([{'product':'P','style':'demo','rating':4,'rating_source':'synthetic','price_tier':'demo'}])
    inventory = pd.DataFrame([{'store':'A','product':'P','on_hand':0}])
    locations = pd.DataFrame([
        {'location':'Depot','lat':43.7,'lon':-79.4,'containers':0,'storage_capacity':1000,'is_depot':True},
        {'location':'Site','lat':43.8,'lon':-79.5,'containers':800,'storage_capacity':1000,'is_depot':False},
    ])
    return sales,catalog,inventory,locations


def test_monthly_evidence():
    answer,traces = analyze_question('monthly sales change',*fixtures())
    assert '2026-01' in answer and '2026-02' in answer
    assert traces[0]['tool']=='sales_breakdown(month)'


def test_no_fake_llm_answer():
    answer,traces = analyze_question('what is the meaning of life?',*fixtures())
    assert 'not recognized' in answer
    assert traces==[]


def test_products():
    answer,traces = analyze_question('products with lowest gross margins',*fixtures())
    assert 'P' in answer and traces


def test_collection():
    answer,traces = analyze_question('plan recycling pickups',*fixtures())
    assert 'Site' in answer and traces
