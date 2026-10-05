from __future__ import annotations

from pyspark.sql import SparkSession
from pyspark.sql import functions as F

from src.config import Settings


def run_consumer(settings: Settings) -> None:
    spark = (
        SparkSession.builder.appName("GTFSRealtimeConsumer")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0")

        .config("spark.hadoop.io.native.lib.available", "false")
        .getOrCreate()
    )

    spark.sparkContext.setLogLevel("WARN")

    df = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", settings.kafka_bootstrap_servers)
        .option("subscribe", settings.kafka_topic)
        .option("startingOffsets", "latest")
        .load()
    )

    record_schema = (
        "feed_timestamp LONG, records ARRAY<STRUCT<id STRING, timestamp LONG, "
        "trip_id STRING, route_id STRING, vehicle_id STRING, latitude DOUBLE, "
        "longitude DOUBLE, bearing DOUBLE, speed DOUBLE, "
        "current_stop_sequence INT, occupancy_status INT, status INT, "
        "is_deleted BOOLEAN, schedule_relationship INT>>"
    )
    feed = df.select(
        F.from_json(F.decode(F.col("value"), "utf-8"), record_schema).alias("data")
    ).select("data.*")
    parsed = (
        feed.select(
            "feed_timestamp",
            F.explode("records").alias("vehicle"),
        )
        .select("feed_timestamp", "vehicle.*")
        .withColumn("event_time", F.to_timestamp(F.from_unixtime("timestamp")))
    )

    query = (
        parsed.writeStream.outputMode("append")
        .format("parquet")
        .option("path", settings.spark_output_path)
        .option("checkpointLocation", f"{settings.spark_output_path}/_checkpoint")
        .queryName("gtfs_realtime_stream")
        .start()
    )

    print(f"Uruchomiono konsument Spark dla topicu: {settings.kafka_topic}")
    query.awaitTermination()


if __name__ == "__main__":
    from src.config import load_settings

    run_consumer(load_settings())
