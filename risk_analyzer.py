"""
This module checks weather forecasts against specific activities (like outdoor sports 
or picnics) to identify risk factors and determine safety levels (Safe, Manageable, Risky, or Avoid).

"""

class ActivityRiskAnalyzer:
    def __init__(self, forecast, activity: str):
        self.forecast = forecast
        self.activity = activity.lower().strip()

    def assess_risk(self) -> str:
        """Evaluates overall risk level: Safe, Manageable, Risky, Avoid."""
        factors = self.get_risk_factors()
        
        has_severe_factor = False
        for f in factors:
            if "Severe" in f or "Extreme" in f or "Thunderstorm" in f:
                has_severe_factor = True
                break

        if has_severe_factor:
            return "Avoid"


        has_high_factor = False
        for f in factors:
            if "High" in f:
                has_high_factor = True
                break
        if len(factors) >= 2 or has_high_factor:
            return "Risky"


        if len(factors) == 1:
            return "Manageable"

        else:
            return "Safe"

    def get_risk_factors(self) -> list:
        """Evaluates weather against specific activity threshold rules."""
        factors = []
        try:
            summary = self.forecast.get_condition_summary()
            
            
            if self.forecast.hourly:
                temp_list = []
                for h in self.forecast.hourly:
                    temp_list.append(h["temp_c"])
                max_temp = max(temp_list)
            else:
                max_temp = 25

            if self.forecast.hourly:
                rain_list = []
                for h in self.forecast.hourly:
                    rain_list.append(h["rain_chance"])
                max_rain = max(rain_list)
            else:
                max_rain = 0

                
            if self.forecast.hourly:
                wind_list = []
                for h in self.forecast.hourly:
                    wind_list.append(h["wind_speed"])
                max_wind = max(wind_list)
            else:
                max_wind = 0

            
            has_storm = False

            if self.forecast.hourly:
                for h in self.forecast.hourly:
                    condition_text = h.get("condition", "").lower()
                    if "thunderstorm" in condition_text:
                        has_storm = True
                        break

            if has_storm:
                factors.append("Severe risk: Thunderstorms detected in forecast")

            if self.activity in ["football", "jogging"]:
                if max_temp > 35:
                    factors.append(f"High heat exposure ({max_temp}°C)")
                if max_rain > 60:
                    factors.append(f"High precipitation probability ({max_rain}%)")
                if max_wind > 40:
                    factors.append(f"Strong winds ({max_wind} km/h)")

            elif self.activity == "farming":
                if max_temp > 38:
                    factors.append(f"Extreme heat stress ({max_temp}°C)")
                elif max_rain > 80:
                    factors.append(f"Heavy rainfall risk ({max_rain}%)")

            elif self.activity in ["picnic", "outdoor event"]:
                if max_rain > 40:
                    factors.append(f"Rain likelihood affects outdoor gathering ({max_rain}%)")
                if max_wind > 30:
                    factors.append(f"Windy conditions ({max_wind} km/h)")

            elif self.activity == "travelling":
                if max_wind > 45:
                    factors.append(f"High winds affecting road safety ({max_wind} km/h)")
                if max_rain > 75:
                    factors.append(f"Reduced road visibility due to heavy rain ({max_rain}%)")

        except Exception as e:
            factors.append("Unable to verify full risk factors due to missing/malformed forecast fields.")

        return factors