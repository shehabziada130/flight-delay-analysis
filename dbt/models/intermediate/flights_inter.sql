{{ config(
    materialized='table',
    schema='intermediate'
) }}
SELECT f.flight_number,f.flight_status,f.flight_date, f.airline_icao,f.airline_name,
f.departure_scheduled,f.departure_actual,f.departure_delay,f.departure_iata,f.departure_airport,
f.arrival_scheduled, f.arrival_actual, f.arrival_delay,f.arrival_iata,f.arrival_airport,
dep_w.precipitation as departure_precipitation,
dep_w.airport_iata as departure_airport_iata, dep_w.wind_speed as departure_wind_speed,dep_w.temperature as departure_temperature,
arr_w.precipitation as arrival_precipitation,
arr_w.airport_iata as arrival_airport_iata, arr_w.wind_speed as arrival_wind_speed, arr_w.temperature as arrival_temperature
FROM `project-c3e2a443-8c7b-4a5f-806.skywatch_stg.stg_flights` f
LEFT JOIN `project-c3e2a443-8c7b-4a5f-806.skywatch_stg.stg_weather_daily` dep_w
ON f.departure_iata = dep_w.airport_iata AND  f.flight_date = dep_w.weather_date
LEFT JOIN `project-c3e2a443-8c7b-4a5f-806.skywatch_stg.stg_weather_daily` arr_w
ON f.arrival_iata = arr_w.airport_iata AND DATE(f.arrival_scheduled) = arr_w.weather_date