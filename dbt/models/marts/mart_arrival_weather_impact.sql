{{
    config(
        materialized='view',
        schema='marts'
    )
}}

SELECT arrival_precipitation, arrival_wind_speed, arrival_temperature,
AVG(IFNULL(arrival_delay,0)) AS avg_arrival_delay,
AVG(IFNULL(departure_delay,0)) AS avg_departure_delay
FROM {{ ref('flights_inter') }}
GROUP BY arrival_precipitation, arrival_wind_speed, arrival_temperature
ORDER BY avg_arrival_delay DESC