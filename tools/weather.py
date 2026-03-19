# tools/weather.py
# Weather tool — fetches current weather data from wttr.in (free, no API key needed).
# Returns a formatted weather summary for any city.

import requests


def get_weather(city: str) -> str:
    """
    Fetch current weather for the given city using the wttr.in JSON API.
    Returns a JARVIS-style natural language weather report.
    """
    city = city.strip()
    if not city:
        return "Please specify a city name, Sir."

    try:
        # wttr.in provides a free JSON weather API — no key required
        url = f"https://wttr.in/{city.replace(' ', '+')}?format=j1"
        response = requests.get(url, timeout=8)
        response.raise_for_status()
        data = response.json()

        # Extract current conditions from the response
        current = data["current_condition"][0]
        weather_desc = current["weatherDesc"][0]["value"]
        temp_c       = current["temp_C"]
        temp_f       = current["temp_F"]
        feels_like_c = current["FeelsLikeC"]
        humidity     = current["humidity"]
        wind_kmph    = current["windspeedKmph"]
        visibility   = current["visibility"]

        # Extract location info
        area = data["nearest_area"][0]
        area_name    = area["areaName"][0]["value"]
        country      = area["country"][0]["value"]

        return (
            f"Current conditions in {area_name}, {country}, Sir:\n"
            f"  Weather   : {weather_desc}\n"
            f"  Temp      : {temp_c}°C / {temp_f}°F (feels like {feels_like_c}°C)\n"
            f"  Humidity  : {humidity}%\n"
            f"  Wind      : {wind_kmph} km/h\n"
            f"  Visibility: {visibility} km"
        )

    except requests.exceptions.ConnectionError:
        return "I'm unable to reach the weather service, Sir. Please check your internet connection."
    except requests.exceptions.Timeout:
        return "The weather service timed out, Sir. Please try again."
    except (KeyError, IndexError, ValueError):
        return f"I couldn't parse weather data for '{city}', Sir. Please verify the city name."
    except requests.exceptions.HTTPError as e:
        return f"Weather service returned an error, Sir: {e}"
    except Exception as e:
        return f"An unexpected error occurred while fetching weather, Sir: {e}"
