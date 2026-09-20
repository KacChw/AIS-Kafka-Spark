from __future__ import annotations

import argparse

from src.config import load_settings
from src.kafka_producer import run_producer
from src.spark_consumer import run_consumer


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="GTFS Realtime streaming pipeline")
    parser.add_argument(
        "--mode",
        choices=["producer", "consumer"],
        required=True,
        help="Run producer to fetch GTFS feed or consumer to read Kafka stream.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    settings = load_settings()

    if args.mode == "producer":
        run_producer(settings)
    else:
        run_consumer(settings)


if __name__ == "__main__":
    main()
