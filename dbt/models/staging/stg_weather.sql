{{ config(
    materialized='view',
    schema='stg'
) }}


SELECT precipitation, weathercode, airport_iata, wind_speed, temperature, timestamp 
FROM `project-c3e2a443-8c7b-4a5f-806.skywatch_raw.weather_raw`
