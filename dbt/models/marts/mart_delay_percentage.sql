{{
    config
    (
        materialized='view',
        schema='marts'
    )
}}

SELECT 
    COUNT(CASE WHEN arrival_delay > 0 THEN 1 END) AS arrival_delayed_flights,
    COUNT(CASE WHEN departure_delay > 0 THEN 1 END) AS departure_delayed_flights,
    CAST(COUNT(*) AS FLOAT64) AS total_flights,
    (COUNT(CASE WHEN arrival_delay > 0 THEN 1 END) / CAST(COUNT(*) AS FLOAT64)) * 100 AS arrival_delay_percentage,
    (COUNT(CASE WHEN departure_delay > 0 THEN 1 END) / CAST(COUNT(*) AS FLOAT64)) * 100 AS departure_delay_percentage,
    (((COUNT(CASE WHEN arrival_delay > 0 THEN 1 END) + COUNT(CASE WHEN departure_delay > 0 THEN 1 END))) / CAST(COUNT(*) AS FLOAT64))* 100 AS total_delay_percentage
FROM {{ ref('flights_inter') }}
