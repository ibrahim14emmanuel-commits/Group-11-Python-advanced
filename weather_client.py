"""
This module connects to the Open-Meteo API to convert location names into GPS coordinates 
and fetch raw weather forecast data.

"""

import requests

class LocationNotFoundError(Exception):
    """Raised when the geocoding API returns no results for location."""
    pass

class WeatherAPIError(Exception):
    """Raised when Open-Meteo returns non-200 HTTP response status."""
    pass

class WeatherClient:
    def __init__(self):
        self.geo_url = "https://geocoding-api.open-meteo.com/v1/search"
        self.forecast_url = "https://api.open-meteo.com/v1/forecast"

    def get_coordinates(self, location_name: str) -> dict:
        """Converts location name into lat/lon via Geocoding API."""
        try:
            params = {"name": location_name, "count": 1, "language": "en", "format": "json"}
            response = requests.get(self.geo_url, params=params, timeout=10)
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.ConnectionError("Failed to connect to network. Check internet connection.")
        except requests.exceptions.Timeout:
            raise requests.exceptions.Timeout("Geocoding API request timed out.")

        if response.status_code != 200:
            raise WeatherAPIError(f"Geocoding API failed with status code {response.status_code}")

        data = response.json()
        if not data.get("results"):
            raise LocationNotFoundError(f"Location '{location_name}' could not be found.")

        result = data["results"][0]
        return {
            "name": result.get("name"),
            "latitude": result.get("latitude"),
            "longitude": result.get("longitude"),
            "country": result.get("country", "")
        }

    def get_forecast(self, lat: float, lon: float) -> dict:
        """Returns the raw forecast JSON from Open-Meteo."""
        parameters = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,precipitation_probability,windspeed_10m,weathercode",
            "daily": "temperature_2m_max,temperature_2m_min",
            "timezone": "auto"
        }
        try:
            response = requests.get(self.forecast_url, params=parameters, timeout=10)
        except requests.exceptions.ConnectionError:
            raise requests.exceptions.ConnectionError("Failed to connect to network. Check internet connection.")
        except requests.exceptions.Timeout:
            raise requests.exceptions.Timeout("Forecast API request timed out.")

        if response.status_code != 200:
            raise WeatherAPIError(f"Forecast API failed with status code {response.status_code}")

        return response.json()

    def fetch_weather(self, location_name: str) -> dict:
        """Convenience method combining coordinate lookup and forecast retrieval."""
        coordinate = self.get_coordinates(location_name)
        forecast_raw = self.get_forecast(coordinate["latitude"], coordinate["longitude"])
        forecast_raw["location_name"] = coordinate["name"]
        return forecast_raw