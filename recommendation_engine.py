import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class RecommendationEngine:
    def __init__(self, api_key: str = None):
        # 1. Use passed key if provided, 2. Otherwise load from .env, 3. Default to None
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if self.api_key:
            genai.configure(api_key=self.api_key)

    def generate_explanation(self, activity: str, risk_level: str, risk_factors: list) -> str:
        """Queries Gemini API for concise natural language explanation, fallback on failure."""
        prompt = (
            f"The user wants to do '{activity}'. The risk level is evaluated as '{risk_level}'. "
            f"Identified risk factors: {', '.join(risk_factors) if risk_factors else 'None'}. "
            "Explain in 2-3 friendly sentences why this risk assessment was given and provide practical guidance."
        )

        if self.api_key:
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                response = model.generate_content(prompt)
                if response and response.text:
                    return response.text.strip()
            except Exception:
                pass  # Gracefully fall through to rule-based fallback on API failure

        # Rule-based fallback mechanism required by project specs
        if risk_level == "Safe":
            return f"Conditions look great for {activity}! Enjoy your time outdoors with standard preparation."
        elif risk_level == "Manageable":
            return f"You can proceed with {activity}, but keep an eye on minor factors: {', '.join(risk_factors)}."
        elif risk_level == "Risky":
            return f"Caution is advised for {activity}. Key concerns include {', '.join(risk_factors)}. Consider adjusting plans."
        else:
            return f"It is strongly recommended to avoid {activity} during this timeframe due to severe conditions: {', '.join(risk_factors)}."

    def recommend_best_time(self, hourly_forecast: list, activity: str) -> str:
        """Scans hourly forecast to recommend best contiguous time window."""
        if not hourly_forecast:
            return "No hourly detail available."

        best_hour = min(
            hourly_forecast,
            key=lambda x: (x.get("rain_chance", 0), abs(x.get("temp_c", 25) - 22))
        )
        time_str = best_hour.get("time", "06:00")
        
        try:
            hour_num = int(time_str.split(":")[0])
            end_hour = (hour_num + 2) % 24
            return f"{hour_num:02d}:00 - {end_hour:02d}:00"
        except Exception:
            return f"Around {time_str}"