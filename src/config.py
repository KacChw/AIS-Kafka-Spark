from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Settings:
    gtfs_realtime_url: str
    kafka_bootstrap_servers: str
    kafka_topic: str
    spark_output_path: str
    poll_interval_seconds: int


def load_settings() -> Settings:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")

    return Settings(
        gtfs_realtime_url=os.getenv("GTFS_REALTIME_URL", "https://example.com/gtfs-realtime"),
        kafka_bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
        kafka_topic=os.getenv("KAFKA_TOPIC", "gtfs.realtime"),
        spark_output_path=os.getenv("SPARK_OUTPUT_PATH", "./data/output"),
        poll_interval_seconds=int(os.getenv("POLL_INTERVAL_SECONDS", "10")),
    )
