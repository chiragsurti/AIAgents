# filename: weather_analysis.py
import requests
import datetime

def get_weather_data(latitude, longitude, location_name):
    # Base URL for Open-Meteo API
    base_url = "https://api.open-meteo.com/v1/forecast"
    
    # Get current weather
    current_params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max",
        "timezone": "auto",
        "start_date": datetime.date.today().isoformat(),
        "end_date": datetime.date.today().isoformat(),
    }
    current_response = requests.get(base_url, params=current_params)
    current_data = current_response.json()
    
    # Get historical weather for the past 30 days
    start_date = (datetime.date.today() - datetime.timedelta(days=30)).isoformat()
    end_date = datetime.date.today().isoformat()
    historical_params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": "temperature_2m_max",
        "timezone": "auto",
        "start_date": start_date,
        "end_date": end_date,
    }
    historical_response = requests.get(base_url, params=historical_params)
    historical_data = historical_response.json()
    
    # Parse current and historical data
    try:
        current_max_temp = current_data["daily"]["temperature_2m_max"][0]
        historical_max_temps = historical_data["daily"]["temperature_2m_max"]
        
        print(f"Weather Data for {location_name}:")
        print(f"Current Max Temperature: {current_max_temp}°C")
        print(f"Historical Max Temperatures (Past Month): {historical_max_temps}")
        return current_max_temp, historical_max_temps
    except KeyError:
        print(f"Error retrieving data for {location_name}. Please check the API response:")
        print("Current Data:", current_data)
        print("Historical Data:", historical_data)

# Coordinates for Arizona and New York
locations = [
    {"name": "Arizona", "latitude": 34.0489, "longitude": -111.0937},
    {"name": "New York", "latitude": 40.7128, "longitude": -74.0060},
]

# Fetch weather data for both locations
for location in locations:
    get_weather_data(location["latitude"], location["longitude"], location["name"])