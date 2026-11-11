import pandas as pd
import pytest
from pathlib import Path
from beeriq.fleet import build_fleet_schedule, snapshot, fleet_summary

BASE = Path(__file__).resolve().parents[1]

@pytest.fixture
def loc():
    return pd.read_csv(BASE / 'data/synthetic_collection_locations.csv')

def test_departure_is_empty(loc):
    s = build_fleet_schedule(loc, truck_capacity=3500, vehicle_count=5, priority_threshold=.6)
    trucks, sites, events = snapshot(s, 0)
    assert len(trucks) > 0
    assert trucks.containers_onboard.sum() == 0
    assert len(events) == 0
    assert sites.collected.sum() == 0

def test_eventual_delivery_balances(loc):
    s = build_fleet_schedule(loc, truck_capacity=3500, vehicle_count=5, priority_threshold=.6)
    t, sites, events = snapshot(s, s['duration_minutes'] + 1)
    collected = events.loc[events.event == 'Containers collected', 'containers'].sum()
    delivered = events.loc[events.event == 'Arrived at depot', 'containers'].sum()
    assert collected == delivered
    assert t.containers_onboard.sum() == 0
    assert sites.remaining.min() == 0
    assert collected == sum(x['expected_load'] for x in s['fleet'])

def test_cargo_never_exceeds_capacity(loc):
    s = build_fleet_schedule(loc, truck_capacity=3500, vehicle_count=5, priority_threshold=.6)
    for minute in range(0, s['duration_minutes'] + 1, 5):
        t, _, _ = snapshot(s, minute)
        assert (t.containers_onboard <= t.capacity).all()
        assert (t.containers_onboard >= 0).all()

def test_event_ledger_non_decreasing(loc):
    s = build_fleet_schedule(loc, truck_capacity=3500, vehicle_count=5, priority_threshold=.6)
    counts = [fleet_summary(s, minute)['containers_collected'] for minute in range(0, s['duration_minutes'] + 1, 10)]
    assert counts == sorted(counts)

def test_impossible_speed_and_negative_time(loc):
    with pytest.raises(ValueError):
        build_fleet_schedule(loc, speed_kmh=0)
    with pytest.raises(ValueError):
        snapshot(build_fleet_schedule(loc), -1)

def test_no_routes_is_safe(loc):
    loc = loc.copy()
    loc.loc[~loc.is_depot, 'containers'] = 0
    s = build_fleet_schedule(loc, priority_threshold=.72)
    t, sites, ev = snapshot(s, 0)
    assert t.empty and sites.empty and ev.empty
