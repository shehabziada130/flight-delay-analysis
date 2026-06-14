{{ config(
    materialized='view',
    schema='stg'
) }}


SELECT  flight_number,	airline_icao,	flight_status,	
CAST(arrival_actual AS TIMESTAMP) AS arrival_actual,
arrival_scheduled,
departure_airport,
arrival_iata,
airline_name ,
flight_date,
CAST(departure_delay AS FLOAT64) AS departure_delay,
CAST(departure_actual AS TIMESTAMP) AS departure_actual, 
arrival_airport,
departure_scheduled,
CAST(arrival_delay AS FLOAT64) AS arrival_delay,	
departure_iata,
ingestion_timestamp	

FROM `project-c3e2a443-8c7b-4a5f-806.skywatch_raw.flights_raw`