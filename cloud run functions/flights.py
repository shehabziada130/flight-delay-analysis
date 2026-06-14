import requests
import json
import os
from datetime import datetime, timezone
from google.cloud import storage


API_KEY = os.environ["AVIATIONSTACK_KEY"]


MENA_AIRPORTS = {
    "ALG","ORN","CZL",
    "BAH","CAI","HBE",
    "HRG","SSH","LXR",
    "IKA","THR","MHD",
    "SYZ","IFN","BGW",
    "EBL","BSR","ISU",
    "NJF","TLV","ETM","HFA","AMM","AQJ","ADJ",
    "KWI","BEY","MCT","SLL","OHS",
    "GZA","DOH","JED","RUH","DMM","MED","AHB",
    "DAM","ALP","LTK",
    "IST","SAW","ESB","AYT",
    "ADB","DXB","AUH",
    "SHJ","DWC","RKT",
    "SAH","ADE","GXF"
}


def get_flights():
    url = "http://api.aviationstack.com/v1/flights"

    response = requests.get(
        url,
        params={"access_key": API_KEY, "limit": 100},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def filter_to_mena(data, ingestion_ts):
    flights = []

    for flight in data.get("data", []):
        dep = flight.get("departure", {})
        arr = flight.get("arrival", {})

        dep_iata = dep.get("iata")
        arr_iata = arr.get("iata")

        if not dep_iata or not arr_iata:
            continue

        if dep_iata in MENA_AIRPORTS or arr_iata in MENA_AIRPORTS:
            flights.append({
                "flight_date": flight.get("flight_date"),
                "flight_status": flight.get("flight_status"),
                "departure_airport": dep.get("airport"),
                "departure_iata": dep_iata,
                "departure_scheduled": dep.get("scheduled"),
                "departure_actual": dep.get("actual"),
                "departure_delay": dep.get("delay"),
                "arrival_airport": arr.get("airport"),
                "arrival_iata": arr_iata,
                "arrival_scheduled": arr.get("scheduled"),
                "arrival_actual": arr.get("actual"),
                "arrival_delay": arr.get("delay"),
                "airline_name": flight.get("airline", {}).get("name"),
                "airline_icao": flight.get("airline", {}).get("icao"),
                "flight_number": flight.get("flight", {}).get("number"),
                "ingestion_timestamp": ingestion_ts,
            })

    return flights


def save_to_gcs(records, bucket_name, timestamp):
    client = storage.Client()
    bucket = client.bucket(bucket_name)

    safe_ts = timestamp.replace(":", "-")
    filename = f"flights_{safe_ts}.jsonl"

    blob = bucket.blob(f"raw/{filename}")

    data = "\n".join(json.dumps(r) for r in records)
    blob.upload_from_string(data, content_type="application/jsonl")

    return filename


def run_flights(bucket_name="mena_flight_data_raw"):
    ingestion_ts = datetime.now(timezone.utc).isoformat()

    raw = get_flights()
    filtered = filter_to_mena(raw, ingestion_ts)

    filename = save_to_gcs(filtered, bucket_name, ingestion_ts)

    print(f"[FLIGHTS] Saved {len(filtered)} records → {filename}")

    return {
        "count": len(filtered),
        "file": filename,
        "timestamp": ingestion_ts,
    }