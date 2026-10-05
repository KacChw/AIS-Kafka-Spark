from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import load_settings
from src.dashboard_data import load_observations


settings = load_settings()
DATA_PATH = Path(settings.spark_output_path)


st.set_page_config(page_title="GTFS Realtime | Monitoring", layout="wide")
st.title("GTFS Realtime")
st.caption(f"Strumień pojazdów · dane z {DATA_PATH}")


@st.cache_data(ttl=8)
def cached_observations(data_path: str):
    return load_observations(data_path)


@st.fragment(run_every="10s")
def show_dashboard() -> None:
    try:
        data = cached_observations(str(DATA_PATH))
    except Exception as error:
        st.error(f"Nie udało się odczytać danych Parquet: {error}")
        return

    if data.empty:
        st.info("Brak danych. Uruchom Kafka oraz producenta i konsumenta Spark.")
        return

    if "is_deleted" in data:
        data = data[data["is_deleted"].fillna(False) == False]

    latest_timestamp = data["feed_timestamp"].max()
    latest = data[data["feed_timestamp"] == latest_timestamp].copy()
    latest["vehicle_key"] = latest["vehicle_id"].fillna(latest["id"])
    latest_speed = latest["speed_kmh"].dropna()
    snapshot_time = pd.to_datetime(latest_timestamp, unit="s", utc=True)

    metric_columns = st.columns(5)
    metric_columns[0].metric("Pojazdy", f"{latest['vehicle_key'].nunique():,}")
    metric_columns[1].metric("Trasy", f"{latest['route_id'].nunique():,}")
    metric_columns[2].metric(
        "Średnia prędkość", f"{latest_speed.mean():.1f} km/h" if not latest_speed.empty else "brak danych"
    )
    metric_columns[3].metric(
        "Maks. prędkość", f"{latest_speed.max():.1f} km/h" if not latest_speed.empty else "brak danych"
    )
    metric_columns[4].metric("Rekordy", f"{len(data):,}")
    st.caption(f"Ostatni snapshot: {snapshot_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")

    chart_left, chart_right = st.columns(2)
    timeline = (
        data.dropna(subset=["event_time", "vehicle_key"])
        .groupby("event_time", as_index=False)["vehicle_key"]
        .nunique()
        .rename(columns={"vehicle_key": "vehicles"})
        .sort_values("event_time")
        .tail(300)
    )
    with chart_left:
        st.subheader("Liczba pojazdów w czasie")
        st.line_chart(timeline, x="event_time", y="vehicles", height=320)

    speed_timeline = (
        data.dropna(subset=["event_time", "speed_kmh"])
        .groupby("event_time", as_index=False)["speed_kmh"]
        .mean()
        .sort_values("event_time")
        .tail(300)
    )
    with chart_right:
        st.subheader("Średnia prędkość w czasie")
        st.line_chart(speed_timeline, x="event_time", y="speed_kmh", height=320)

    st.subheader("Pozycje pojazdów")
    positions = latest.dropna(subset=["latitude", "longitude"]).copy()
    positions = positions[
        positions["latitude"].between(-90, 90)
        & positions["longitude"].between(-180, 180)
        & ~((positions["latitude"] == 0) & (positions["longitude"] == 0))
    ]
    positions = positions.drop_duplicates(subset=["vehicle_key"])
    if positions.empty:
        st.info("Najnowszy snapshot nie zawiera pozycji latitude/longitude.")
    else:
        positions["speed_label"] = positions["speed_kmh"].round(1)
        figure = px.scatter_mapbox(
            positions,
            lat="latitude",
            lon="longitude",
            color="speed_label",
            hover_name="vehicle_key",
            hover_data={"route_id": True, "speed_label": ":.1f", "latitude": ":.5f", "longitude": ":.5f"},
            labels={"speed_label": "Prędkość (km/h)"},
            zoom=10,
            height=520,
            color_continuous_scale="Turbo",
        )
        figure.update_layout(mapbox_style="open-street-map", margin={"r": 0, "t": 0, "l": 0, "b": 0})
        st.plotly_chart(figure, use_container_width=True)


show_dashboard()
