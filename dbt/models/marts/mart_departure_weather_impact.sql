{{
    config(
        materialized='view',
        schema='marts'
    )
}}

SELECT departure_precipitation, departure_wind_speed, departure_temperature,
AVG(IFNULL(arrival_delay,0)) AS avg_arrival_delay,
AVG(IFNULL(departure_delay,0)) AS avg_departure_delay
FROM {{ ref('flights_inter') }}
GROUP BY departure_precipitation, departure_wind_speed, departure_temperature
ORDER BY avg_departure_delay DESC