"""Recreate demonstration CSVs deterministically. Data is fictional, never company operational data."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent / 'data'
ROOT.mkdir(exist_ok=True)
rng = np.random.default_rng(20261112)
products = [
 ('Classic Lager A','Lager',3.7,'Illustrative synthetic rating','Value',3.60,2.45),
 ('Crisp Lager B','Lager',4.0,'Illustrative synthetic rating','Mainstream',3.90,2.60),
 ('Northern Pilsner','Pilsner',4.2,'Illustrative synthetic rating','Premium',4.65,3.00),
 ('Golden Lager C','Lager',3.5,'Illustrative synthetic rating','Value',3.20,2.25),
 ('Amber Ale A','Amber Ale',4.4,'Illustrative synthetic rating','Premium',4.95,3.10),
 ('Session Pale Ale','Pale Ale',4.3,'Illustrative synthetic rating','Premium',5.10,3.30),
 ('West Coast IPA','IPA',4.6,'Illustrative synthetic rating','Premium',5.75,3.65),
 ('Hazy IPA A','IPA',4.7,'Illustrative synthetic rating','Premium',5.95,4.20),
 ('Wheat Style A','Wheat',4.0,'Illustrative synthetic rating','Mainstream',4.40,2.95),
 ('Dark Stout A','Stout',4.6,'Illustrative synthetic rating','Premium',5.35,3.40),
 ('Dry Stout B','Stout',4.1,'Illustrative synthetic rating','Mainstream',4.50,3.10),
 ('Porter A','Porter',4.5,'Illustrative synthetic rating','Premium',5.15,3.15),
 ('Brown Ale A','Brown Ale',4.2,'Illustrative synthetic rating','Mainstream',4.30,2.80),
 ('Citrus Wheat B','Wheat',3.8,'Illustrative synthetic rating','Mainstream',4.05,2.95),
 ('Pale Ale B','Pale Ale',4.1,'Illustrative synthetic rating','Mainstream',4.50,3.05),
 ('Light Lager D','Lager',3.4,'Illustrative synthetic rating','Value',3.35,2.30),
 ('Malt Style A','Malt',3.9,'Illustrative synthetic rating','Mainstream',4.10,2.70),
 ('Seasonal Craft A','Seasonal',4.8,'Illustrative synthetic rating','Premium',6.25,4.15),
]
cat = pd.DataFrame(products,columns=['product','style','rating','rating_source','price_tier','unit_price','unit_cost'])
cat.to_csv(ROOT/'synthetic_catalog.csv', index=False)
stores = ['Toronto Central','Toronto West','Mississauga','Brampton','Hamilton','Oakville','Burlington','Milton']
rows = []
start = pd.Timestamp('2026-04-01')
for i in range(12500):
    date = start + pd.Timedelta(days=int(rng.integers(0,210)))
    store = str(rng.choice(stores))
    idx = int(rng.choice(len(cat), p=(lambda w: w/w.sum())(np.array([.14,.10,.05,.11,.04,.05,.045,.03,.045,.04,.04,.03,.04,.05,.05,.08,.045,.025]))))
    product = cat.iloc[idx]
    units = int(rng.choice([1,2,3,4,6,12],p=[.19,.37,.18,.12,.10,.04]))
    # Deliberately illustrate margin pressure in recent premium products.
    cost = float(product.unit_cost) + (0.4 if date >= pd.Timestamp('2026-09-01') and product.price_tier == 'Premium' else 0)
    rows.append([date.date().isoformat(), store, product['product'], units, float(product.unit_price), round(cost,2)])
pd.DataFrame(rows,columns=['date','store','product','units','unit_price','unit_cost']).to_csv(ROOT/'synthetic_sales.csv', index=False)
inv=[]
for s in stores:
    for p in cat['product']:
        inv.append([s,p,int(rng.integers(12,95))])
pd.DataFrame(inv,columns=['store','product','on_hand']).to_csv(ROOT/'synthetic_inventory.csv',index=False)
# Coordinates approximate cities, not actual The Beer Store facilities.
locations=[
 ('Illustrative Depot (Toronto)',43.680,-79.390,0,99999,True),
 ('Toronto Central Point',43.653,-79.383,1750,2200,False),
 ('Toronto West Point',43.655,-79.475,1220,1600,False),
 ('Mississauga Point',43.589,-79.644,1870,2000,False),
 ('Brampton Point',43.731,-79.763,1130,1500,False),
 ('Hamilton Point',43.256,-79.872,1040,1600,False),
 ('Oakville Point',43.468,-79.688,650,1500,False),
 ('Burlington Point',43.325,-79.800,870,1100,False),
 ('Milton Point',43.519,-79.878,500,1600,False),
]
pd.DataFrame(locations,columns=['location','lat','lon','containers','storage_capacity','is_depot']).to_csv(ROOT/'synthetic_collection_locations.csv',index=False)
print('Wrote synthetic catalog, sales, inventory and collection locations')
