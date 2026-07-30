import os
from datetime import date

import streamlit as st

from checklist_generator import ChecklistGenerator
from forecast import Forecast
from recommendation_engine import RecommendationEngine
from risk_analyzer import ActivityRiskAnalyzer
from storage import StorageManager
from validators import validate_activity, validate_date, validate_location
from weather_client import WeatherClient


ACTIVITIES = [
    "football",
    "jogging",
    "farming",
    "picnic",
    "travelling",
    "outdoor event",
]

RISK_LABELS = {
    "safe": "🟢 Safe",
    "manageable": "🟡 Manageable",
    "risky": "🟠 Risky",
    "avoid": "🔴 Avoid",
}


st.set_page_config(
    page_title="Weather Risk Planner",
    page_icon="🌦️",
    layout="wide",
)


try:
    storage = StorageManager()
except Exception as error:
    storage = None
    st.sidebar.error(f"Storage error: {error}")


st.sidebar.title("🌦️ Weather Planner")
st.sidebar.subheader("Saved Favourites")

saved_locations = []

if storage:
    try:
        saved_locations = storage.get_favourites()
    except Exception as error:
        st.sidebar.error(f"Could not load favourites: {error}")

if saved_locations:
    for location in saved_locations:
        st.sidebar.write(f"⭐ {location}")
elif storage:
    st.sidebar.caption("No saved locations yet.")
else:
    st.sidebar.caption("Storage is unavailable.")


st.sidebar.divider()
st.sidebar.subheader("Recent Searches")

search_history = []

if storage:
    try:
        search_history = storage.get_history()
    except Exception as error:
        st.sidebar.error(f"Could not load history: {error}")

if search_history:
    recent_searches = reversed(search_history[-5:])

    for search in recent_searches:
        history_location = search.get("location", "Unknown")
        history_activity = search.get("activity", "")
        history_date = search.get("date", "")

        st.sidebar.markdown(
            f"📍 **{history_location}**  \n"
            f"{history_activity.title()} — {history_date}"
        )
else:
    st.sidebar.caption("No search history yet.")


st.title("🌦️ Weather Risk & Outdoor Activity Planner")
st.write(
    "Check the weather risk, recommended time and items "
    "to take for an outdoor activity."
)


with st.form("weather_form"):
    location_input = st.text_input(
        "Location",
        placeholder="For example: Abuja",
    )

    selected_activity = st.selectbox(
        "Outdoor Activity",
        ACTIVITIES,
        format_func=str.title,
    )

    selected_date = st.date_input(
        "Date",
        value=date.today(),
    )

    submitted = st.form_submit_button(
        "Analyze Weather",
        use_container_width=True,
    )


if submitted:
    try:
        location = validate_location(location_input)
        activity = validate_activity(selected_activity, ACTIVITIES)

        date_string = selected_date.strftime("%Y-%m-%d")
        validate_date(date_string)

        with st.spinner("Checking the weather..."):
            weather_client = WeatherClient()
            weather_response = weather_client.fetch_weather(location)

            forecast = Forecast(weather_response)
            forecast.parse()

            selected_day = forecast.get_forecast_for_date(date_string)

            if selected_day is None:
                st.warning("No forecast is available for that date.")
                st.stop()

            analyzer = ActivityRiskAnalyzer(forecast, activity)
            risk_level = analyzer.assess_risk()
            risk_factors = analyzer.get_risk_factors()

            gemini_key = os.getenv("GEMINI_API_KEY")

            if not gemini_key:
                st.error("Add GEMINI_API_KEY to your environment variables.")
                st.stop()

            recommendation_engine = RecommendationEngine(
                api_key=gemini_key
            )

            recommendation = (
                recommendation_engine.generate_explanation(
                    activity,
                    risk_level,
                    risk_factors,
                )
            )

            best_time = recommendation_engine.recommend_best_time(
                selected_day,
                activity,
            )

            checklist_generator = ChecklistGenerator(
                forecast,
                activity,
            )

            packing_list = checklist_generator.generate()

        if storage:
            try:
                storage.log_search(
                    {
                        "location": location,
                        "activity": activity,
                        "date": date_string,
                        "risk": risk_level,
                        "best_time": best_time,
                    }
                )
            except Exception as error:
                st.warning(f"Could not save this search: {error}")

        st.success("Weather analysis completed.")
        st.header(f"Weather Plan for {location}")
        st.info(forecast.get_condition_summary())

        normalized_risk = str(risk_level).lower()
        risk_display = RISK_LABELS.get(
            normalized_risk,
            f"⚪ {str(risk_level).title()}",
        )

        risk_section, time_section = st.columns(2)

        with risk_section:
            st.metric("Activity Risk", risk_display)

        with time_section:
            st.metric("Recommended Time", best_time)

        st.divider()
        st.subheader("Risk Factors")

        if risk_factors:
            for factor in risk_factors:
                st.write(f"- {factor}")
        else:
            st.write("No major weather risks were detected.")

        st.subheader("AI Recommendation")
        st.write(recommendation)

        st.subheader("Packing Checklist")

        if packing_list:
            left_column, right_column = st.columns(2)
            checklist_columns = [left_column, right_column]

            for index, item in enumerate(packing_list):
                target_column = checklist_columns[index % 2]

                with target_column:
                    st.checkbox(
                        item,
                        key=f"packing_item_{index}",
                    )
        else:
            st.write("No special items are required.")

        st.divider()

        if storage and st.button("Save Location as Favourite"):
            try:
                storage.add_favourite(location)
                st.success(f"{location} was added to favourites.")
            except Exception as error:
                st.error(f"Could not save location: {error}")

    except ValueError as error:
        st.error(str(error))

    except Exception as error:
        st.error(f"Weather analysis failed: {error}")