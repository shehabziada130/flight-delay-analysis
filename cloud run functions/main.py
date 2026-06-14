from weather import run_weather
from flights import run_flights


def opensky(request):

    weather_files = run_weather()
    flights_result = run_flights()

    print(f"Weather files: {len(weather_files)}")
    print(f"Flights: {flights_result['count']}")

    return f"Processed {len(weather_files)} weather files and {flights_result['count']} flights.", 200

