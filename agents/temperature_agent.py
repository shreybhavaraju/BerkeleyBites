"""
Temperature Agent for BerkeleyBites

Gets current Berkeley weather and provides temperature-based food suggestions.
Uses Open-Meteo API as a free weather service.
"""

import os
import requests
from langchain_core.tools import tool

# Berkeley, CA coordinates
BERKELEY_LAT = 37.8716
BERKELEY_LON = -122.2727

# Temperature thresholds (Fahrenheit)
COLD_THRESHOLD = 55
COOL_THRESHOLD = 65
WARM_THRESHOLD = 75
HOT_THRESHOLD = 85


def get_temperature_guidance(temp_f: float) -> dict:
    """Get food guidance based on temperature."""
    if temp_f < COLD_THRESHOLD:
        return {
            "description": f"It's cold outside ({temp_f:.0f}°F)",
            "food_suggestion": "Perfect weather for warming foods! Hot soups, stews, warm grain bowls, and hot beverages will help you feel cozy.",
            "prefer_types": ["hot soups", "stews", "hot beverages", "warm entrees", "baked dishes"],
            "avoid_types": ["cold salads", "ice cream", "cold sandwiches"],
        }
    elif temp_f < COOL_THRESHOLD:
        return {
            "description": f"It's cool outside ({temp_f:.0f}°F)",
            "food_suggestion": "Nice weather for a mix of warm and room-temperature foods. Warm sandwiches, grain bowls, or light soups work well.",
            "prefer_types": ["warm dishes", "grain bowls", "light soups", "warm sandwiches"],
            "avoid_types": [],
        }
    elif temp_f < WARM_THRESHOLD:
        return {
            "description": f"It's pleasantly warm ({temp_f:.0f}°F)",
            "food_suggestion": "Great weather for almost anything! Both warm and cool options work well. Follow your mood and preferences.",
            "prefer_types": ["any"],
            "avoid_types": [],
        }
    elif temp_f < HOT_THRESHOLD:
        return {
            "description": f"It's warm outside ({temp_f:.0f}°F)",
            "food_suggestion": "Lighter, refreshing foods are ideal. Fresh salads, cold sandwiches, and lighter proteins. Stay hydrated!",
            "prefer_types": ["salads", "cold dishes", "light proteins", "fresh fruits", "smoothies"],
            "avoid_types": ["heavy hot dishes", "fried foods"],
        }
    else:
        return {
            "description": f"It's hot outside ({temp_f:.0f}°F)",
            "food_suggestion": "Beat the heat with cold, refreshing options! Salads, cold sandwiches, fresh fruits, and plenty of water. Avoid heavy, hot foods.",
            "prefer_types": ["cold salads", "fresh fruits", "cold beverages", "light cold dishes", "ice cream"],
            "avoid_types": ["hot soups", "heavy hot entrees", "fried foods"],
        }


def fetch_weather_from_open_meteo() -> dict:
    """
    Fetch current weather from Open-Meteo API (free, no API key required).

    Returns:
        dict with temperature_f and conditions, or error info
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": BERKELEY_LAT,
            "longitude": BERKELEY_LON,
            "current": "temperature_2m,weather_code",
            "temperature_unit": "fahrenheit",
            "timezone": "America/Los_Angeles",
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        current = data.get("current", {})
        temp_f = current.get("temperature_2m", 65)  # Default to 65°F

        # Weather codes: https://open-meteo.com/en/docs
        weather_code = current.get("weather_code", 0)
        conditions = interpret_weather_code(weather_code)

        return {
            "success": True,
            "temperature_f": temp_f,
            "conditions": conditions,
            "source": "Open-Meteo",
        }

    except requests.RequestException as e:
        return {
            "success": False,
            "error": str(e),
            "temperature_f": 65,  # Fallback temperature
            "conditions": "unknown (API unavailable)",
            "source": "fallback",
        }


def interpret_weather_code(code: int) -> str:
    """Interpret Open-Meteo weather code to human-readable condition."""
    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        95: "Thunderstorm",
    }
    return weather_codes.get(code, "Unknown conditions")


@tool
def get_current_temperature() -> str:
    """
    Get the current temperature in Berkeley and food suggestions based on weather.

    Fetches real-time weather data and provides temperature-appropriate
    food recommendations.

    Returns:
        A string with current temperature and food suggestions.
    """
    weather = fetch_weather_from_open_meteo()
    temp_f = weather["temperature_f"]
    conditions = weather["conditions"]
    source = weather["source"]

    guidance = get_temperature_guidance(temp_f)

    result = f"""Current Weather in Berkeley, CA:
Temperature: {temp_f:.0f}°F
Conditions: {conditions}
Data Source: {source}

{guidance['description']}

Food Guidance: {guidance['food_suggestion']}

Recommended food types: {', '.join(guidance['prefer_types'])}
Food types to avoid: {', '.join(guidance['avoid_types']) if guidance['avoid_types'] else 'None'}"""

    if not weather["success"]:
        result += f"\n\nNote: Weather API was unavailable. Using estimated temperature."

    return result
