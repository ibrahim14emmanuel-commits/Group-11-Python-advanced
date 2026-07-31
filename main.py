

import streamlit as st
import datetime
from validators import validate_location, validate_date, validate_activity, InvalidLocationError, InvalidDateError, InvalidActivityError
from weather_client import WeatherClient, LocationNotFoundError, WeatherAPIError
from forecast import Forecast
from risk_analyzer import ActivityRiskAnalyzer
from recommendation_engine import RecommendationEngine
from checklist_generator import ChecklistGenerator
from storage import StorageManager

st.set_page_config(page_title="Weather Risk & Outdoor Activity Planner", page_icon="🌤️", layout="wide")

# App Setup
ALLOWED_ACTIVITIES = ["football", "jogging", "farming", "picnic", "travelling", "outdoor event"]
storage = StorageManager()
client = WeatherClient()
rec_engine = RecommendationEngine(api_key=None)  # Add Gemini API key if available

if "analyzed_data" not in st.session_state:
    st.session_state.analyzed_data = None

st.title("🌤️ Weather Risk & Outdoor Activity Planner")

# Sidebar - Favourites & History
with st.sidebar:
    st.header("📌 Saved Favourites")
    favs = storage.get_favourites()
    if favs:
        for fav in favs:
            st.write(f"- {fav}")
    else:
        st.info("No saved favourite locations yet.")

    st.markdown("---")
    st.header("🕒 Recent Search History")
    history = storage.get_history()
    if history:
        for rec in history[:5]:
            st.caption(f"**{rec.get('location')}** | {rec.get('activity')} ({rec.get('date')})")
            st.caption(f"Status: {rec.get('risk_level')}")
            st.markdown("---")

# Main Form Setup
with st.form("planner_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        location_input = st.text_input("Enter Location", value="Abuja")
    with col2:
        activity_input = st.selectbox("Select Outdoor Activity", options=ALLOWED_ACTIVITIES)
    with col3:
        date_input = st.date_input("Select Date", value=datetime.date.today())

    submit_button = st.form_submit_button("Analyze Plan")

# Processing pipeline on submit
if submit_button:
    try:
        # Step 1: Input Validation
        valid_loc = validate_location(location_input)
        date_str = date_input.strftime("%Y-%m-%d")
        validate_date(date_str)
        valid_activity = validate_activity(activity_input, ALLOWED_ACTIVITIES)

        # Step 2: Fetch Raw Weather Data
        raw_weather = client.fetch_weather(valid_loc)

        # Step 3: Parse weather objects via Person 2's Forecast class
        forecast_obj = Forecast(raw_weather)

        # Step 4: Analyze Risk
        analyzer = ActivityRiskAnalyzer(forecast_obj, valid_activity)
        risk_level = analyzer.assess_risk()
        risk_factors = analyzer.get_risk_factors()

        # Step 5: Recommendations
        ai_explanation = rec_engine.generate_explanation(valid_activity, risk_level, risk_factors)
        best_time = rec_engine.recommend_best_time(forecast_obj.hourly, valid_activity)

        # Step 6: Checklist Generation
        checklist_gen = ChecklistGenerator(forecast_obj, valid_activity)
        packing_list = checklist_gen.generate()

        # Step 7: Storage Persistence
        search_record = {
            "location": valid_loc,
            "activity": valid_activity,
            "date": date_str,
            "risk_level": risk_level
        }
        storage.log_search(search_record)

        st.session_state.analyzed_data = {
            "valid_loc": valid_loc,
            "date_str": date_str,
            "risk_level": risk_level,
            "ai_explanation": ai_explanation,
            "best_time": best_time,
            "risk_factors": risk_factors,
            "packing_list": packing_list
        }

    except (InvalidLocationError, InvalidDateError, InvalidActivityError) as ve:
        st.error(f"Input Validation Error: {ve}")
    except LocationNotFoundError as le:
        st.warning(f"Location Error: {le}")
    except WeatherAPIError as we:
        st.error(f"Weather API Error: {we}")
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")

if st.session_state.analyzed_data:
    data = st.session_state.analyzed_data

    # Step 8: Render Results
    st.subheader(f"Results for {data['valid_loc'].capitalize()} ({data['date_str']})")
    
    # Color coding metrics
    risk_colors = {"Safe": "green", "Manageable": "blue", "Risky": "orange", "Avoid": "red"}
    st.markdown(f"### Overall Risk Status: :{risk_colors.get(data['risk_level'], 'gray')}[{data['risk_level']}]")
    
    st.info(f"**AI Recommendation:** {data['ai_explanation']}")
    st.success(f"⏰ **Best Recommended Time Window:** {data['best_time']}")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### Identified Risk Factors")
        if data['risk_factors']:
            for rf in data['risk_factors']:
                st.write(f"- {rf}")
        else:
            st.write("No specific risks found.")

    with col_b:
        st.markdown("#### Recommended Packing Checklist")
        for item in data['packing_list']:
            st.checkbox(item, key=f"chk_{item}")

    if st.button("Save Location as Favourite"):
        storage.add_favourite(data['valid_loc'])
        st.success(f"Saved {data['valid_loc']} to Favourites!")
        st.rerun()
