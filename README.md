# Projekt Data Engineer: GTFS Realtime w czasie rzeczywistym

To jest przykład projektu data engineering do pobierania i przetwarzania danych GTFS Realtime z API transportu publicznego w czasie rzeczywistym.

## Cel projektu

- pobieranie danych o położeniu pojazdów i aktualizacjach tras,
- publikacja danych do Kafka,
- przetwarzanie strumieniowe w Spark,
- zapis wyników do formatu Parquet,
- dashboard ze statystykami i wizualizacją pozycji.

## Architektura

```text
GTFS Realtime API
        |
        v
Python Producer -> Kafka -> Spark Structured Streaming -> Parquet -> Streamlit Dashboard
```

## Główne komponenty

- `main.py` – punkt wejścia do uruchamiania producenta lub konsumenta,
- `dashboard.py` – dashboard ze statystykami i wykresami na podstawie zapisanych danych,
- `src/gtfs_realtime_client.py` – pobieranie i normalizacja danych z feedu GTFS,
- `src/kafka_producer.py` – wysyłka danych do Kafka,
- `src/spark_consumer.py` – odczyt strumieniowy z Kafka i zapis jednego wiersza Parquet na pojazd,
- `docker-compose.yml` – środowisko Kafka + ZooKeeper,
- `.env.example` – przykładowa konfiguracja środowiska.

## Wymagania

- Python 3.10+
- Docker i Docker Compose
- Apache Kafka
- Apache Spark

## Instalacja

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

## Konfiguracja

Skopiuj plik `.env.example` do `.env` i uzupełnij adres API GTFS.

```powershell
Copy-Item .env.example .env
```

Przykładowe parametry:

```env
GTFS_REALTIME_URL=https://example.com/gtfs-realtime
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC=gtfs.realtime
SPARK_OUTPUT_PATH=./data/output
```

## Uruchomienie

Uruchom Kafka:

```bash
docker compose up -d
```

Uruchom producenta i konsumenta Spark w osobnych terminalach:

```bash
python main.py --mode producer
python main.py --mode consumer
```

Uruchom dashboard w kolejnym terminalu:

```bash
streamlit run dashboard.py
```

Dashboard odświeża dane co 10 sekund i pokazuje:

- liczbę pojazdów i tras z najnowszego snapshotu,
- średnią i maksymalną prędkość z najnowszego snapshotu (km/h; feed GTFS podaje m/s),
- łączną liczbę zapisanych obserwacji,
- liczbę pojazdów oraz średnią prędkość w czasie,
- pozycje pojazdów na mapie OpenStreetMap.

## Przykładowy rekord danych

```json
{
  "timestamp": 1720000000,
  "trip_id": "123",
  "route_id": "10",
  "vehicle_id": "A12",
  "latitude": 54.352,
  "longitude": 18.646,
  "speed": 16.4,
  "bearing": 92.0,
  "status": "IN_TRANSIT_TO"
}
```

## Kolejne kroki

1. podmienić przykładowy URL na realne źródło GTFS Realtime,
2. dodać dane o przystankach i trasach z GTFS Static,
3. zbudować model opóźnień i odległości do przystanków,
4. dodać walidację jakości danych i alerty,
5. zapisać wyniki do lakehouse / warehouse / Delta table.

## Przykładowe źródła GTFS Realtime

- GTFS Realtime API operatora transportu miejskiego,
- Open Mobility Data,
- publiczne API komunikacji miejskiej.

## Uwaga

W praktyce należy stosować własne, autoryzowane źródło danych oraz zgodnie z polityką dostawcy API.
