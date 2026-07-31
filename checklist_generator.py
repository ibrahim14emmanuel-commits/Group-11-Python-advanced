"""

This module builds a smart packing checklist by checking the weather forecast 
and the user's planned activity, then returning a clean list of needed items.

"""

class ChecklistGenerator:
    def __init__(self, forecast, activity: str):
        self.forecast = forecast
        self.activity = activity.lower().strip()

    def generate(self) -> list:
        """Generates a combined, de-duplicated list of packing items based on weather & activity."""
        items = set()



        if self.forecast.hourly:
            hourly_temperatures = []
            for h in self.forecast.hourly:
                hourly_temperatures.append(h["temp_c"])
            max_temp = max(hourly_temperatures)
        else:
            max_temp = 25


        if self.forecast.hourly:
            hourly_temperatures = []
            for h in self.forecast.hourly:
                hourly_temperatures.append(h["temp_c"])
            min_temp = min(hourly_temperatures)
        else:
            min_temp = 25


        if self.forecast.hourly:
            rain_chances = []
            for h in self.forecast.hourly:
                rain_chances.append(h["rain_chance"])
            max_rain = max(rain_chances)
        else:
            max_rain = 0
        max_wind = max([h["wind_speed"] for h in self.forecast.hourly]) if self.forecast.hourly else 0


        if max_rain > 50:
            items.update(["Umbrella", "Raincoat", "Waterproof bag"])
        if max_temp > 30:
            items.update(["Sunscreen", "Extra water bottle", "Hat / Cap"])
        if min_temp < 15:
            items.update(["Jacket", "Gloves"])
        if max_wind > 30:
            items.update(["Windbreaker"])

        activity_items = {
            "football": ["Cleats", "Shin guards", "Sports towel"],
            "jogging": ["Running shoes", "Sweatband", "Hydration pack"],
            "farming": ["Work boots", "Heavy-duty gloves", "Wide-brim hat"],
            "picnic": ["Picnic blanket", "Cooler box", "Reusable cutlery"],
            "travelling": ["First-aid kit", "Power bank", "Travel documents"],
            "outdoor event": ["Portable seat / chair", "Power bank", "Sunglasses"]
        }

        items.update(activity_items.get(self.activity, ["General supplies"]))

        return sorted(list(items))