"""

This module is the "translator" between the raw JSON that WeatherClient (Section 1)
gets back from Open-Meteo, and clean, structured data that the rest of the app can use
without ever touching a messy dictionary of arrays.

"""

import re
from datetime import datetime

class Forecast:
    """
        Takes the raw dictionary returned from Open-Meteo's native raw JSON shape and turns it
        into clean, structured, easy-to-use data.
    
        """
    # WMO Weather Interpretation Codes (Open-Meteo standard)
    WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snowfall",
    73: "Moderate snowfall",
    75: "Heavy snowfall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
    }

    def __init__(self, raw_weather_data: dict):
        self.raw = raw_weather_data
        self.hourly = []
        self.daily = []
        self.location_name = raw_weather_data.get("location_name", "Unknown Location")
        self.parse()

    def parse(self):
        """Parses raw Open-Meteo dictionary into clean hourly and daily structures."""
        hourly_raw = self.raw.get("hourly", {})
        times = hourly_raw.get("time", [])
        temps = hourly_raw.get("temperature_2m", [])
        rain_chances = hourly_raw.get("precipitation_probability", [])
        wind_speeds = hourly_raw.get("windspeed_10m", [])
        codes = hourly_raw.get("weathercode", [])

        for i in range(len(times)):
            time_str = times[i]
            # Convert ISO timestamp "YYYY-MM-DDTHH:MM" to datetime object
            dt_obj = datetime.fromisoformat(time_str)
            
            if i < len(codes):
                wmo_code = codes[i]
            else:
                wmo_code = 0
                
            condition_text = self.WMO_CODES.get(wmo_code, "Unknown")

            entry = {
                "datetime": dt_obj,
                "date": dt_obj.strftime("%Y-%m-%d"),
                "time": dt_obj.strftime("%H:%M"),
                "temp_c": float(temps[i]) if i < len(temps) else 0.0,
                "condition": condition_text,
                "wind_speed": float(wind_speeds[i]) if i < len(wind_speeds) else 0.0,
                "rain_chance": int(rain_chances[i]) if i < len(rain_chances) else 0
            }
            self.hourly.append(entry)

        # 2. Parse Daily Forecast Data
        daily_raw = self.raw.get("daily", {})
        daily_times = daily_raw.get("time", [])
        max_temps = daily_raw.get("temperature_2m_max", [])
        min_temps = daily_raw.get("temperature_2m_min", [])

        for i in range(len(daily_times)):
            date_val = daily_times[i]

            if i < len(max_temps):
                temp_max_val = float(max_temps[i])
            else:
                temp_max_val = 0.0

            if i < len(min_temps):
                temp_min_val = float(min_temps[i])
            else:
                temp_min_val = 0.0

            daily_entry = {
                "date": date_val,
                "temp_max": temp_max_val,
                "temp_min": temp_min_val,
            }

            self.daily.append(daily_entry)

    def extract_numeric_value(self, text: str) -> float:
        """Uses Regex to extract numeric values out of text descriptions (e.g. pulling 22 from '22 km/h')."""
        match = re.search(r"[-+]?\d*\.\d+|\d+", str(text))
        if match:
            return float(match.group())
        return 0.0

    def get_forecast_for_date(self, date_str: str) -> list:
        """Returns all hourly forecast entries for one specific date (YYYY-MM-DD)."""
        matching_hours = []
    
        for h in self.hourly:
            if h["date"] == date_str:
                matching_hours.append(h)
                
        return matching_hours

def get_condition_summary(self) -> str:
    """Returns a human-readable summary string of upcoming weather conditions."""
    if not self.hourly:
        return "No weather data available."

    rain_chances = []
    temperatures = []
    conditions = []

    for h in self.hourly:
        rain_chances.append(h["rain_chance"])
        temperatures.append(h["temp_c"])
        conditions.append(h["condition"])

    max_rain = max(rain_chances)
    max_temp = max(temperatures)
    min_temp = min(temperatures)

    unique_conditions = set(conditions) #sets remove duplicates which is why it was used
    most_frequent_condition = None
    highest_count = 0

    for condition in unique_conditions:
        count = conditions.count(condition)
        if count > highest_count:
            highest_count = count
            most_frequent_condition = condition

    condition_text = most_frequent_condition.lower()
    location = self.location_name

    summary_sentence_1 = f"Expect mostly {condition_text} conditions in {location}. "
    summary_sentence_2 = f"Temperatures ranging from {min_temp:.1f}°C to {max_temp:.1f}°C with up to {max_rain}% chance of rain."

    return summary_sentence_1 + summary_sentence_2


