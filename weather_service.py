"""
app/services/weather_service.py
================================
Fetches current weather from OpenWeatherMap API.
Falls back to demo data if no API key is set.

Usage:
    from app.services.weather_service import weather_service
    data = weather_service.get_weather("Nagpur")
"""
from __future__ import annotations
import requests
from app.config import settings


class WeatherService:

    def get_weather(self, city: str, units: str = "metric") -> dict:
        """
        Fetch current weather for a city.
        Returns dict with: city, temperature, feels_like, humidity,
                           description, wind_speed, summary
        """
        if not settings.OPENWEATHER_API_KEY:
            return self._demo(city)

        url    = f"{settings.OPENWEATHER_BASE_URL}/weather"
        params = {
            "q":     city,
            "appid": settings.OPENWEATHER_API_KEY,
            "units": units,
        }

        try:
            r = requests.get(url, params=params, timeout=5)
            r.raise_for_status()
            d = r.json()
        except requests.exceptions.ConnectionError:
            return {"error": "No internet connection."}
        except requests.exceptions.HTTPError:
            if r.status_code == 404:
                return {"error": f"City '{city}' not found. Check the spelling."}
            return {"error": f"Weather API error: {r.status_code}"}
        except requests.exceptions.Timeout:
            return {"error": "Weather request timed out."}
        except Exception as e:
            return {"error": f"Unexpected error: {e}"}

        info = {
            "city":        d["name"],
            "temperature": d["main"]["temp"],
            "feels_like":  d["main"]["feels_like"],
            "humidity":    d["main"]["humidity"],
            "description": d["weather"][0]["description"].capitalize(),
            "wind_speed":  d["wind"]["speed"],
        }
        info["summary"] = self._advisory(info)
        return info

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _advisory(w: dict) -> str:
        """Generate a farming advisory from weather data."""
        lines = [
            f"🌤️  {w['city']}: {w['description']}",
            f"🌡️  Temp: {w['temperature']}°C  (feels {w['feels_like']}°C)",
            f"💧  Humidity: {w['humidity']}%   💨 Wind: {w['wind_speed']} m/s",
        ]
        desc = w["description"].lower()
        h    = w["humidity"]
        t    = w["temperature"]

        if "rain" in desc or "drizzle" in desc:
            lines.append("🌧️  Advisory: Rain expected — skip irrigation today.")
        elif h < 30:
            lines.append("⚠️  Advisory: Low humidity — consider irrigating crops.")
        elif t > 38:
            lines.append("🔥  Advisory: Very hot — water crops early morning or evening.")
        elif t < 10:
            lines.append("❄️  Advisory: Cold — protect sensitive seedlings.")
        else:
            lines.append("✅  Advisory: Good conditions for fieldwork today.")

        return "\n".join(lines)

    @staticmethod
    def _demo(city: str) -> dict:
        """Placeholder when no API key is set."""
        return {
            "city":        city,
            "temperature": 28,
            "feels_like":  30,
            "humidity":    65,
            "description": "Partly cloudy (demo mode — no API key)",
            "wind_speed":  3.5,
            "summary": (
                f"🌤️  {city}: Partly cloudy (demo mode)\n"
                "✅  Add OPENWEATHER_API_KEY to .env for live weather."
            ),
        }


# ── Singleton — import this object everywhere ─────────────────────────────────
weather_service = WeatherService()