{{
    config(
        materialized='view',
        schema='marts',
    )
}}

SELECT EXTRACT(HOUR FROM arrival_scheduled) AS arrival_hour,AVG(arrival_delay) AS avg_arrival_delay
FROM {{ ref('flights_inter') }}
GROUP BY EXTRACT(HOUR FROM arrival_scheduled)