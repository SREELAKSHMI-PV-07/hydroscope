# services/weather.py

import requests
import streamlit as st


@st.cache_data(ttl=600)
def get_weather(lat, lon):

    try:
        api_key = st.secrets["OPENWEATHER_API_KEY"]
    except Exception:
        return {
            "success": False,
            "error": "OpenWeather API key is not configured."
        }

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code == 401:
            return {
                "success": False,
                "error": "OpenWeather API key is not active yet."
            }

        if response.status_code == 429:
            return {
                "success": False,
                "error": "OpenWeather API request limit reached."
            }

        response.raise_for_status()

        data = response.json()

        rainfall = 0.0

        if "rain" in data:
            rainfall = data["rain"].get("1h", 0.0)

        return {
            "success": True,

            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],

            "wind_speed": data["wind"]["speed"],

            "rainfall": rainfall,

            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],

            "city": data.get("name", "Unknown")
        }

    except requests.exceptions.RequestException as e:

        return {
            "success": False,
            "error": f"Weather service unavailable: {e}"
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }
