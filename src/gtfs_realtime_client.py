from __future__ import annotations

import json
import time
from typing import Any

import requests

try:
    from google.transit import gtfs_realtime_pb2
except ImportError:  # pragma: no cover
    try:
        import gtfs_realtime_pb2
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "Brak biblioteki GTFS Realtime. Zainstaluj zależności z requirements.txt."
        ) from exc


def fetch_gtfs_feed(url: str) -> dict[str, Any]:
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)

    records: list[dict[str, Any]] = []
    for entity in feed.entity:
        vehicle = entity.vehicle
        if not vehicle:
            continue

        trip_update = entity.trip_update
        vehicle_record = {
            "id": entity.id,
            "timestamp": feed.header.timestamp if feed.header.timestamp else int(time.time()),
            "trip_id": vehicle.trip.trip_id if vehicle.trip.trip_id else None,
            "route_id": vehicle.trip.route_id if vehicle.trip.route_id else None,
            "vehicle_id": vehicle.vehicle.id if vehicle.vehicle.id else None,
            "latitude": vehicle.position.latitude if vehicle.position else None,
            "longitude": vehicle.position.longitude if vehicle.position else None,
            "bearing": vehicle.position.bearing if vehicle.position else None,
            "speed": vehicle.position.speed if vehicle.position else None,
            "current_stop_sequence": vehicle.current_stop_sequence,
            "occupancy_status": vehicle.occupancy_status,
            "status": vehicle.current_status,
            "is_deleted": entity.is_deleted,
        }

        if trip_update and trip_update.trip:
            vehicle_record["schedule_relationship"] = trip_update.trip.schedule_relationship

        records.append(vehicle_record)

    return {
        "feed_timestamp": feed.header.timestamp if feed.header.timestamp else int(time.time()),
        "records": records,
    }


def fetch_feed_payload(url: str) -> bytes:
    payload = fetch_gtfs_feed(url)
    return json.dumps(payload).encode("utf-8")
