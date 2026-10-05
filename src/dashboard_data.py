from __future__ import annotations

from pathlib import Path

import pandas as pd


def load_observations(data_path: str) -> pd.DataFrame:
    root = Path(data_path)
    parquet_files = [
        file_path
        for file_path in root.rglob("*.parquet")
        if "_checkpoint" not in file_path.parts
    ] if root.exists() else []

    frames = []
    for file_path in parquet_files:
        frame = pd.read_parquet(file_path)
        if "records" in frame.columns:
            frame = frame.explode("records", ignore_index=True).dropna(subset=["records"])
            record_fields = pd.json_normalize(frame.pop("records"))
            frame = pd.concat([frame.reset_index(drop=True), record_fields], axis=1)
        frames.append(frame)

    if not frames:
        return pd.DataFrame()

    data = pd.concat(frames, ignore_index=True)
    if "feed_timestamp" not in data and "timestamp" in data:
        data["feed_timestamp"] = data["timestamp"]
    for column in ("id", "vehicle_id", "speed"):
        if column not in data:
            data[column] = None
    data["event_time"] = pd.to_datetime(
        data["feed_timestamp"], unit="s", utc=True, errors="coerce"
    )
    data["vehicle_key"] = data["vehicle_id"].fillna(data["id"])
    data["speed_kmh"] = pd.to_numeric(data["speed"], errors="coerce") * 3.6
    return data
