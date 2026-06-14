import requests
import json
from datetime import datetime, timezone
from google.cloud import storage


def load_airports():
    with open("iata_lat_lon.json") as f:
        return json.load(f)


def get_weather_data(lat, lon):
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&hourly=temperature_2m,precipitation,weathercode"
        "&current_weather=true"
    )

    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def filter_weather_data(weather_data,iata):
    current = weather_data.get("current_weather", {})
    hourly = weather_data.get("hourly", {})

    precipitation = hourly.get("precipitation", [])
    avg_precip = sum(precipitation) / len(precipitation) if precipitation else 0

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "airport_iata":iata,
        "temperature": current.get("temperature"),
        "wind_speed": current.get("windspeed"),
        "precipitation": avg_precip,
        "weathercode": current.get("weathercode"),
    }


def save_to_gcs(data, bucket_name, filename_prefix, timestamp):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    safe_ts = timestamp.replace(":", "-")
    filename = f"{filename_prefix}_{safe_ts}.jsonl"

    blob = bucket.blob(f"raw/{filename}")
    blob.upload_from_string(
        json.dumps(data) + "\n",
        content_type="application/jsonl",
    )

    return filename


def run_weather(bucket_name="filtered_weather_data"):
    airports = load_airports()
    timestamp = datetime.now(timezone.utc).isoformat()

    saved_files = []

    for iata, (lat, lon) in airports.items():
        try:
            raw = get_weather_data(lat, lon)
            filtered = filter_weather_data(raw,iata)

            filename = save_to_gcs(
                filtered,
                bucket_name=bucket_name,
                filename_prefix=f"weather_{iata}",
                timestamp=timestamp,
            )

            print(f"[WEATHER] Saved {iata} → {filename}")
            saved_files.append(filename)

        except Exception as e:
            print(f"[WEATHER ERROR] {iata}: {e}")

    return saved_files