{{
    config(
        materialized='view',
        schema='marts'
    )
}}

SELECT airline_icao,airline_name, AVG(IFNULL(arrival_delay,0)) AS avg_arrival_delay,
AVG(IFNULL(departure_delay,0)) AS avg_departure_delay
FROM {{ ref('flights_inter') }}
GROUP BY airline_icao,airline_name
ORDER BY avg_arrival_delay DESC