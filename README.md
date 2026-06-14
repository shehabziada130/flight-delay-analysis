# MENA Flight Delay Analysis
 
A small end-to-end pipeline that pulls live flight data for routes connected to MENA airports, joins it with weather conditions at departure and arrival, and surfaces the results in a Looker Studio dashboard. Built to get hands-on with the GCP stack: Cloud Run, Cloud Storage, BigQuery, and dbt.
 
## Business Question
 
For flights tied to MENA airports, what's actually behind the delays?
 
- How many flights run late on departure vs arrival, and by how much?
- Are certain airlines or airports consistently worse than others?
- Is there a pattern by time of day?
- Does weather (precipitation, wind, temperature) at the departure or arrival airport actually move the needle?
## Architecture
 
```
Cloud Scheduler
   ↓
Cloud Run (opensky function)
   ↓
AviationStack API  +  Open-Meteo API
   ↓
Cloud Storage (mena_flight_data_raw / filtered_weather_data)
   ↓
BigQuery Raw (skywatch_raw)
   ↓
dbt staging (skywatch_stg)
   ↓
dbt intermediate (skywatch_intermediate)
   ↓
dbt marts (skywatch_marts)
   ↓
Looker Studio
```
 
The pipeline runs without manual steps: a scheduled trigger fires the ingestion function, which pulls fresh flight and weather data and lands it in Cloud Storage. From there dbt takes over and models it into something the dashboard can read directly.
 
## Data Sources
 
- **AviationStack API** — flight-level data: status, scheduled/actual departure and arrival times, delay in minutes, airline name/ICAO, flight number, and departure/arrival airport.
- **Open-Meteo API** — current weather plus an hourly forecast (temperature, wind speed, precipitation, weather code) per airport. No API key required.
- **iata_lat_lon.json** — a static lookup of latitude/longitude for the 53 MENA airports this project tracks, generated once with `get_iata_lat_lon.py` by joining an airports reference CSV against the list of MENA IATA codes.
## Technologies Used
 
- Python (`requests`, `pandas`, `google-cloud-storage`)
- Google Cloud Run Functions — HTTP-triggered ingestion
- Google Cloud Storage — raw landing zone for JSONL files
- BigQuery — raw, staging, intermediate, and marts datasets
- dbt — modeling layer (project name: `skywatch`)
- Looker Studio — dashboard
## Data Pipeline
 
1. **Cloud Scheduler** hits the Cloud Run function (`opensky`) on a schedule.
2. The function runs two jobs:
   - `run_flights()` calls AviationStack for up to 100 flights, keeps only the ones where the departure or arrival airport is in the MENA set (53 airports spanning Algeria, Egypt, the Gulf states, Iran, Iraq, Israel, Jordan, Lebanon, Syria, Turkey, and Yemen), and writes the result as a JSONL file to the `mena_flight_data_raw` bucket.
   - `run_weather()` loops over all 53 MENA airports, calls Open-Meteo for each one using the precomputed lat/lon, and writes one JSONL file per airport to the `filtered_weather_data` bucket — temperature and wind speed come from the current-weather snapshot, precipitation is averaged from the hourly forecast.
3. The JSONL files get loaded into two BigQuery raw tables: `skywatch_raw.flights_raw` and `skywatch_raw.weather_raw`.
4. dbt picks up from there and builds staging → intermediate → marts.
5. Looker Studio connects directly to the mart tables.


## Data Modeling
 
**Staging** (views, schema `stg`)
- `stg_flights` — selects the flight fields needed downstream and casts `arrival_actual`/`departure_actual` to `TIMESTAMP` and `arrival_delay`/`departure_delay` to `FLOAT64`.
- `stg_weather` — passes through the raw weather rows (precipitation, wind speed, temperature, weather code, timestamp, airport).
- `stg_weather_daily` (table) — collapses `stg_weather` down to one row per airport per day, averaging precipitation, wind speed, and temperature. This is what turns multiple intraday weather snapshots into a single daily value per airport.
**Intermediate** (table, schema `intermediate`)
- `flights_inter` — the core model. Joins `stg_flights` to `stg_weather_daily` twice: once on the departure airport and flight date (departure-side weather), and once on the arrival airport and the date of the scheduled arrival (arrival-side weather). Every mart is built on top of this.
**Marts** (views, schema `marts`)
- `mart_delay_percentage` — total flights, counts of delayed arrivals/departures, and the resulting delay percentages.
- `mart_delay_by_airline` — average arrival and departure delay per airline, sorted worst first.
- `mart_delay_by_airport` — average arrival and departure delay per arrival airport, sorted worst first.
- `mart_arrival_delay_date` — average arrival delay by hour of day.
- `mart_departure_weather_impact` — average delay grouped by departure-airport weather (precipitation, wind speed, temperature).
- `mart_arrival_weather_impact` — same, but grouped by arrival-airport weather.
## Dashboard
 
Two pages, built directly off the mart tables.
 
**Page 1 — overview**
- Four KPI gauges: arrival delay percentage (20.7%), departure delay percentage (1.0%), and total delay percentage (21.3%).
- **Top 20 Delayed Airlines** — bar chart ranking airlines by average delay, topped by TGI at roughly 23 minutes.
- **Top 20 Delayed Airports** — bar chart ranking arrival airports by average delay, topped by Copenhagen Kastrup and Frankfurt at around 24–25 minutes.
- **Most Delayed Hour** — average arrival delay by hour of day, peaking around 5PM (~27 minutes) with smaller peaks near 2AM, 9AM, and 3PM.
**Page 2 — weather impact**
- `avg_arrival_delay` by `arrival_precipitation` — delay drops sharply from around 53 minutes at zero precipitation down to near zero as precipitation increases.
- `avg_arrival_delay` by `arrival_temperature` — similar downward shape, from about 12.5 minutes at the lowest temperature bucket toward zero.
- `arrival_wind_speed` and `avg_arrival_delay` combo chart — delays cluster highest at low wind speed and drop off as wind speed increases.
## Business Questions Answered
 
- What share of flights are delayed on arrival vs departure, and overall? → `mart_delay_percentage`
- Which airlines have the worst average delays? → `mart_delay_by_airline`
- Which arrival airports have the worst average delays? → `mart_delay_by_airport`
- What time of day has the highest average arrival delay? → `mart_arrival_delay_date`
- Does weather at the departure airport correlate with delays? → `mart_departure_weather_impact`
- Does weather at the arrival airport correlate with delays? → `mart_arrival_weather_impact`
