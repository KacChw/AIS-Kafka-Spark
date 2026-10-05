from __future__ import annotations

import pandas as pd

from src.dashboard_data import load_observations


def test_load_observations_returns_empty_for_missing_path(tmp_path) -> None:
    assert load_observations(str(tmp_path / "missing")).empty


def test_load_observations_flattens_metrics_and_converts_speed(tmp_path) -> None:
    pd.DataFrame(
        {
            "feed_timestamp": [1_700_000_000],
            "id": ["entity-1"],
            "vehicle_id": [None],
            "speed": [10.0],
        }
    ).to_parquet(tmp_path / "snapshot.parquet")

    result = load_observations(str(tmp_path))

    assert result.loc[0, "vehicle_key"] == "entity-1"
    assert result.loc[0, "speed_kmh"] == 36.0
    assert result.loc[0, "event_time"] == pd.Timestamp("2023-11-14 22:13:20", tz="UTC")


def test_load_observations_reads_legacy_nested_feed_parquet(tmp_path) -> None:
    pd.DataFrame(
        {
            "feed_timestamp": [1_700_000_000],
            "records": [[
                {"id": "entity-1", "vehicle_id": "bus-1", "route_id": "10", "speed": 5.0},
                {"id": "entity-2", "vehicle_id": "bus-2", "route_id": "20", "speed": 8.0},
            ]],
        }
    ).to_parquet(tmp_path / "legacy.parquet")

    result = load_observations(str(tmp_path))

    assert result["vehicle_id"].tolist() == ["bus-1", "bus-2"]
    assert result["route_id"].nunique() == 2
    assert result["speed_kmh"].tolist() == [18.0, 28.8]
