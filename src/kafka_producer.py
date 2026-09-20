from __future__ import annotations

import json
import time
from typing import Any

from kafka import KafkaProducer

from src.config import Settings
from src.gtfs_realtime_client import fetch_feed_payload


def run_producer(settings: Settings) -> None:
    producer = KafkaProducer(
        bootstrap_servers=[settings.kafka_bootstrap_servers],
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        acks="all",
        retries=3,
    )

    print(f"Uruchomiono producenta Kafka dla topicu: {settings.kafka_topic}")
    print(f"Pobieranie danych z: {settings.gtfs_realtime_url}")

    while True:
        try:
            payload = fetch_feed_payload(settings.gtfs_realtime_url)
            producer.send(settings.kafka_topic, value=json.loads(payload.decode("utf-8")))
            producer.flush()
            print(f"Wysłano rekord GTFS w czasie: {time.strftime('%Y-%m-%d %H:%M:%S')}" )
        except Exception as exc:  # pragma: no cover
            print(f"Błąd pobierania danych GTFS: {exc}")

        time.sleep(settings.poll_interval_seconds)


if __name__ == "__main__":
    from src.config import load_settings

    run_producer(load_settings())
