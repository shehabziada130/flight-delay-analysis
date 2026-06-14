{{
    config(
        materialized='view',
        schema='marts'
    )
}}

SELECT arrival_iata as iata, arrival_airport as airport,AVG(IFNULL(arrival_delay,0)) AS avg_arrival_delay,
AVG(IFNULL(departure_delay,0)) AS avg_departure_delay
FROM {{ ref('flights_inter') }}
GROUP BY iata, airport
ORDER BY avg_arrival_delay DESC