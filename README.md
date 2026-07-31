# Group-11-Python-advanced
WEATHER RISK AND OUTDOOR ACTIVITY PLANNER : an application built in Python that helps users plan outdoor activities safely by analyzing weather forecasts and offering personalized recommendations concerning risk associated with their chosen activity and the weather, and a list of items they ought to caryy along if the activity is safe enough to carry out.

 This is  desktop app that lets you look up a country's public holidays for a given year, compare two countries' holidays side by side, and generate a short AI-written explanation of what any individual holiday means culturally.

Built with Python and streamlit (a python framework) for the GUI, the free OpenMeteo API for weather forecasts, and Google's Gemini API for the literal explanations.

1. USING IT:
Check Activity Risk: Enter a target city/location name, choose an activity (e.g., football, jogging, farming, picnic, travelling, outdoor event), and run the check to view safety ratings (Safe, Manageable, Risky, Avoid) along with specific weather risk factors.

Get AI Guidance & Best Time Window: View Gemini-generated AI explanations detailing why an activity received its specific risk rating, alongside calculated 2-hour optimal time windows for your plans.

Generate Packing Checklist: Get an automatically generated, deduplicated packing list tailored specifically to forecasted extreme weather (heat, rain, wind) and activity gear requirements.

Manage Favorites & View History: Save frequently searched cities to your favorites list for quick lookup, and review automatically logged search history stored locally in data/ which will be created automatically on running the complete project

NOTE: For the code to run successfully,  you need to create a .env file locally and paste your own Gemini API key
2. SET YOUR API KEY:
The app works without a key (weather fetching, risk assessment, packing checklists, and history all still work), but AI explanations rely on one to generate real natural-language guidance. Get a free key from Google AI Studio, then:

Create a file named .env in the project folder containing:
GEMINI_API_KEY = your_key_here


 
