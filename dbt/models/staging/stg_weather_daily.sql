{{
    config(
        materialized='table',
        schema='stg'
    )
}}


SELECT airport_iata,
DATE(timestamp) AS weather_date,AVG(precipitation) AS precipitation, AVG(wind_speed) AS wind_speed,
AVG(temperature) AS temperature
FROM {{ ref('stg_weather') }}
GROUP BY airport_iata,DATE(timestamp)
