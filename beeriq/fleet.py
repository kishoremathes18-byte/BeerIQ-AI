"""Reproducible, synthetic fleet playback and container movement ledger.

NOT GPS or telematics. Travel uses straight-line distances and a fixed demo speed;
route feasibility and regulatory constraints are not represented.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import ceil
import pandas as pd
from .core import haversine, plan_pickups

DEMO_SPEED_KMH = 32.0
STOP_MINUTES = 12


def build_fleet_schedule(locations: pd.DataFrame, truck_capacity: int = 2400,
                         vehicle_count: int = 4, priority_threshold: float = .72,
                         speed_kmh: float = DEMO_SPEED_KMH,
                         stop_minutes: int = STOP_MINUTES) -> dict:
    """Compile routes into ordered synthetic travel / pickup / return segments."""
    if speed_kmh <= 0 or not (0 <= stop_minutes <= 240):
        raise ValueError('Speed must be positive and stop duration between 0 and 240 min')
    if locations.location.duplicated().any():
        raise ValueError('Every location must have a unique name')
    if locations[['lat', 'lon', 'containers', 'storage_capacity']].isna().any().any():
        raise ValueError('Location fields cannot be blank')
    if not locations.lat.between(-90, 90).all() or not locations.lon.between(-180, 180).all():
        raise ValueError('Invalid latitude or longitude')
    plan = plan_pickups(locations, truck_capacity, vehicle_count, priority_threshold)
    depot = locations[locations.is_depot.astype(bool)].iloc[0]
    index = locations.set_index('location')
    fleet = []
    for route in plan['routes']:
        current = (float(depot.lat), float(depot.lon))
        minute = 0.0
        legs = []
        for stop in route['stops']:
            r = index.loc[stop['location']]
            dest = (float(r.lat), float(r.lon))
            distance = haversine(*current, *dest)
            travel = 60 * distance / speed_kmh
            legs.append({'kind': 'drive', 'from': current, 'to': dest, 'start': minute,
                         'end': minute + travel, 'destination': stop['location'],
                         'containers': 0, 'distance_km': distance})
            minute += travel
            legs.append({'kind': 'pickup', 'from': dest, 'to': dest, 'start': minute,
                         'end': minute + stop_minutes, 'destination': stop['location'],
                         'containers': int(stop['containers']), 'distance_km': 0.0})
            minute += stop_minutes
            current = dest
        dest = (float(depot.lat), float(depot.lon))
        distance = haversine(*current, *dest)
        travel = 60 * distance / speed_kmh
        legs.append({'kind': 'return', 'from': current, 'to': dest, 'start': minute,
                     'end': minute + travel, 'destination': str(depot.location),
                     'containers': 0, 'distance_km': distance})
        minute += travel
        fleet.append({'truck_id': f'TRUCK-{route["vehicle"]:03d}', 'capacity': int(truck_capacity),
                      'expected_load': int(route['load']), 'route_stops': [s['location'] for s in route['stops']],
                      'segments': legs, 'finish_minute': round(minute, 2)})
    return {'fleet': fleet, 'plan': plan, 'depot': {'location': str(depot.location),
            'lat': float(depot.lat), 'lon': float(depot.lon)},
            'duration_minutes': max(30, ceil(max((t['finish_minute'] for t in fleet), default=0) / 10) * 10),
            'speed_kmh': speed_kmh, 'stop_minutes': stop_minutes,
            'disclosure': 'SIMULATED fleet locations and container events; no real trucks or GPS. '
                          'Distances and travel times use straight-line approximations, not road routing.'}


def snapshot(schedule: dict, minute: float) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return truck positions, site balances and immutable-through-time event ledger."""
    if minute < 0:
        raise ValueError('Elapsed minutes cannot be negative')
    minute = float(minute)
    fleet_rows, events = [], []
    site_original = {}
    for truck in schedule['fleet']:
        for leg in truck['segments']:
            if leg['kind'] == 'pickup':
                site_original[leg['destination']] = int(leg['containers'])
    for truck in schedule['fleet']:
        legs = truck['segments']
        load = 0
        completed = []
        for leg in legs:
            if leg['kind'] == 'pickup' and minute >= leg['end']:
                load += leg['containers']
                completed.append(leg['destination'])
                events.append({'minute': round(leg['end'], 1), 'truck_id': truck['truck_id'],
                               'event': 'Containers collected', 'location': leg['destination'],
                               'containers': leg['containers']})
        if legs and minute >= legs[-1]['end']:
            events.append({'minute': round(legs[-1]['end'], 1), 'truck_id': truck['truck_id'],
                           'event': 'Arrived at depot', 'location': schedule['depot']['location'],
                           'containers': load})
            status = 'Delivered to depot'
            lat, lon = schedule['depot']['lat'], schedule['depot']['lon']
            next_stop = 'Complete'
            eta = 0
            delivered = load
            onboard = 0
        else:
            delivered = 0
            onboard = load
            leg = next((s for s in legs if minute < s['end']), legs[-1])
            status = 'Collecting containers' if leg['kind'] == 'pickup' else 'Returning to depot' if leg['kind'] == 'return' else 'En route to pickup'
            if leg['kind'] in ('drive', 'return'):
                portion = max(0.0, min(1.0, (minute - leg['start']) / max(.00001, leg['end'] - leg['start'])))
                lat = leg['from'][0] + portion * (leg['to'][0] - leg['from'][0])
                lon = leg['from'][1] + portion * (leg['to'][1] - leg['from'][1])
            else:
                lat, lon = leg['to']
            next_stop = leg['destination']
            eta = max(0, ceil(leg['end'] - minute))
        fleet_rows.append({'truck_id': truck['truck_id'], 'latitude': lat, 'longitude': lon,
                           'status': status, 'next_stop': next_stop, 'eta_minutes': eta,
                           'containers_onboard': onboard, 'containers_delivered': delivered,
                           'capacity': truck['capacity'], 'utilization_pct': round(100 * onboard / truck['capacity'], 1),
                           'completed_pickups': len(completed), 'planned_pickups': len(truck['route_stops'])})
    event_df = pd.DataFrame(events, columns=['minute', 'truck_id', 'event', 'location', 'containers'])
    if not event_df.empty:
        event_df = event_df.sort_values(['minute', 'truck_id']).reset_index(drop=True)
    picked = event_df[event_df.event == 'Containers collected'].groupby('location').containers.sum().to_dict() if not event_df.empty else {}
    site_df = pd.DataFrame([{'location': loc, 'starting_containers': units,
                             'collected': int(picked.get(loc, 0)), 'remaining': units - int(picked.get(loc, 0))}
                            for loc, units in site_original.items()])
    return pd.DataFrame(fleet_rows), site_df, event_df


def fleet_summary(schedule: dict, minute: float) -> dict:
    trucks, sites, events = snapshot(schedule, minute)
    pickups = events[events.event == 'Containers collected'] if not events.empty else events
    delivered = events[events.event == 'Arrived at depot'] if not events.empty else events
    return {'elapsed_minutes': minute, 'trucks_active': int((trucks.status != 'Delivered to depot').sum()),
            'trucks_finished': int((trucks.status == 'Delivered to depot').sum()),
            'containers_collected': int(pickups.containers.sum()),
            'containers_delivered_to_depot': int(delivered.containers.sum()),
            'containers_on_trucks': int(trucks.containers_onboard.sum()),
            'sites_collected': int(len(pickups)),
            'sites_scheduled': int(schedule['plan']['scheduled_locations']),
            'sites_unscheduled': int(len(schedule['plan']['unscheduled'])),
            'estimated_straight_line_km': schedule['plan']['total_distance_km_straight_line'],
            'simulation_only': True}
