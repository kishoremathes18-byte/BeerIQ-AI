"""Validated, deterministic analysis of synthetic or uploaded retail transactions."""
from __future__ import annotations
import math
import pandas as pd

SALES_REQUIRED = {'date', 'store', 'product', 'units', 'unit_price', 'unit_cost'}

def load_sales(df: pd.DataFrame) -> pd.DataFrame:
    missing = SALES_REQUIRED - set(df.columns)
    if missing:
        raise ValueError('Missing required columns: ' + ', '.join(sorted(missing)))
    out = df.copy()
    out['date'] = pd.to_datetime(out['date'], errors='coerce')
    for col in ('units', 'unit_price', 'unit_cost'):
        out[col] = pd.to_numeric(out[col], errors='coerce')
    if out[['date','store','product','units','unit_price','unit_cost']].isna().any().any():
        raise ValueError('Sales file has blank or invalid dates, stores, products, units or prices.')
    if (out['units'] < 0).any() or (out[['unit_price', 'unit_cost']] < 0).any().any():
        raise ValueError('Negative units, prices, and costs are not supported.')
    out['revenue'] = (out.units * out.unit_price).round(2)
    out['cost'] = (out.units * out.unit_cost).round(2)
    out['gross_profit'] = (out.revenue - out.cost).round(2)
    out['month'] = out.date.dt.to_period('M').astype(str)
    return out

def kpis(sales: pd.DataFrame) -> dict:
    revenue = float(sales.revenue.sum())
    profit = float(sales.gross_profit.sum())
    return {'revenue': round(revenue, 2), 'gross_profit': round(profit, 2),
            'gross_margin_pct': round(100 * profit / revenue, 2) if revenue else 0,
            'units': int(sales.units.sum()), 'transactions': int(len(sales)),
            'stores': int(sales.store.nunique())}

def sales_breakdown(sales: pd.DataFrame, dimension: str, limit: int = 15) -> pd.DataFrame:
    if dimension not in ('month','product','store'):
        raise ValueError('dimension must be month, product, or store')
    result = (sales.groupby(dimension, as_index=False)
              .agg(revenue=('revenue','sum'), gross_profit=('gross_profit','sum'), units=('units','sum')))
    result['gross_margin_pct'] = (100 * result.gross_profit / result.revenue.where(result.revenue.ne(0))).fillna(0).round(2)
    return result.sort_values(dimension if dimension == 'month' else 'revenue',
                              ascending=(dimension == 'month')).head(max(1, min(50, limit))).reset_index(drop=True)

def quality_sales(sales: pd.DataFrame, catalog: pd.DataFrame) -> pd.DataFrame:
    summary = sales_breakdown(sales, 'product', 50)
    keep = ['product','style','rating','rating_source','price_tier']
    return summary.merge(catalog[keep], on='product', how='left')

def forecast(sales: pd.DataFrame, store: str, product: str, days: int = 7, lookback: int = 28) -> dict:
    """Naive daily average forecast; no claim of model sophistication or prediction intervals."""
    if days < 1 or days > 90:
        raise ValueError('days must be 1–90')
    end = sales.date.max().normalize()
    subset = sales[(sales.store == store) & (sales['product'] == product)]
    start = end - pd.Timedelta(days=lookback-1)
    daily = subset.groupby(subset.date.dt.normalize()).units.sum()
    recent = daily.reindex(pd.date_range(start, end), fill_value=0)
    predicted = float(recent.mean() * days)
    return {'store':store,'product':product,'forecast_days':days,'historical_days':lookback,
            'estimated_units':round(predicted,1),'daily_average':round(float(recent.mean()),2),
            'method':'28-day trailing daily average, including zero-sales days',
            'caution':'Illustrative baseline. Does not model promotions, stockouts, seasonality or external demand.'}

def stock_priorities(sales: pd.DataFrame, inventory: pd.DataFrame, horizon: int = 7) -> pd.DataFrame:
    rows = []
    for rec in inventory.itertuples(index=False):
        pred = forecast(sales, rec.store, rec.product, days=horizon)
        gap = float(rec.on_hand) - pred['estimated_units']
        rows.append({'store':rec.store,'product':rec.product,'on_hand':int(rec.on_hand),
                     'estimated_demand':pred['estimated_units'],'surplus_units':round(gap,1),
                     'priority':'Review replenishment' if gap < 0 else 'OK'})
    return pd.DataFrame(rows).sort_values('surplus_units').reset_index(drop=True)

def haversine(a_lat: float, a_lon: float, b_lat: float, b_lon: float) -> float:
    r = 6371
    dlat, dlon = math.radians(b_lat-a_lat), math.radians(b_lon-a_lon)
    t = math.sin(dlat/2)**2 + math.cos(math.radians(a_lat))*math.cos(math.radians(b_lat))*math.sin(dlon/2)**2
    return 2*r*math.asin(min(1, math.sqrt(t)))

def plan_pickups(locations: pd.DataFrame, truck_capacity: int = 2400, vehicle_count: int = 3,
                 priority_threshold: float = 0.72) -> dict:
    """Transparent greedy pickup plan. Geographic straight-line distance, NOT road routing."""
    required = {'location','lat','lon','containers','storage_capacity','is_depot'}
    if not required.issubset(locations.columns):
        raise ValueError('Location data missing: '+', '.join(sorted(required-set(locations.columns))))
    if truck_capacity <= 0 or vehicle_count <= 0:
        raise ValueError('Truck capacity and vehicle count must be positive')
    depots = locations[locations.is_depot.astype(bool)]
    if len(depots) != 1:
        raise ValueError('Exactly one depot required')
    depot = depots.iloc[0]
    candidates = locations[~locations.is_depot.astype(bool)].copy()
    if (candidates.storage_capacity <= 0).any() or (candidates.containers < 0).any():
        raise ValueError('Invalid site inventory or capacity')
    candidates['utilization'] = candidates.containers/candidates.storage_capacity
    selected = candidates[candidates.utilization >= priority_threshold].sort_values('utilization', ascending=False)
    remaining = {r.location: r for r in selected.itertuples(index=False)}
    routes = []
    for t in range(vehicle_count):
        left = truck_capacity
        cur_lat, cur_lon = float(depot.lat), float(depot.lon)
        distance = 0.
        stops = []
        while left > 0 and remaining:
            feasible = [r for r in remaining.values() if int(r.containers) <= left]
            if not feasible:
                break
            nxt = min(feasible, key=lambda r: haversine(cur_lat, cur_lon, r.lat, r.lon))
            distance += haversine(cur_lat, cur_lon, nxt.lat, nxt.lon)
            cur_lat, cur_lon = nxt.lat, nxt.lon
            left -= int(nxt.containers)
            stops.append({'location':nxt.location,'containers':int(nxt.containers), 'utilization_pct':round(nxt.utilization*100,1)})
            del remaining[nxt.location]
        if stops:
            distance += haversine(cur_lat, cur_lon, depot.lat, depot.lon)
            routes.append({'vehicle':t+1,'stops':stops,'load':truck_capacity-left,
                           'distance_km_straight_line':round(distance,1)})
    unscheduled = [{'location':r.location,'containers':int(r.containers),
                    'reason':'Exceeds available vehicle capacity or insufficient vehicles'}
                   for r in remaining.values()]
    return {'routes':routes,'unscheduled':unscheduled,
            'selected_locations':len(selected),'scheduled_locations':sum(len(r['stops']) for r in routes),
            'total_distance_km_straight_line':round(sum(r['distance_km_straight_line'] for r in routes),1),
            'method':'Greedy nearest-feasible-stop heuristic; straight-line geodesic distances',
            'limitations':'Not road-network distance or guaranteed optimal. No driver shifts, traffic, service windows, partial pickups, or unloading trips.'}
