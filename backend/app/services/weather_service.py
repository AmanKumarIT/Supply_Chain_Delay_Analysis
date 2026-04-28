"""
WeatherService — Fetches live weather data from OpenWeatherMap API
for waypoints along a supply chain route and normalizes them into
a composite severity score for the ML model.
"""
import httpx
import math
from typing import List, Tuple, Dict, Any
from app.core.config import settings


class WeatherService:
    BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

    def __init__(self):
        self.api_key = settings.openweather_api_key

    def _sample_waypoints(
        self, coords: List[List[float]], max_points: int = 5
    ) -> List[Tuple[float, float]]:
        """
        Given a list of [lat, lng] coordinates forming a route,
        sample up to `max_points` evenly-spaced waypoints for weather checks.
        """
        if len(coords) <= max_points:
            return [(c[0], c[1]) for c in coords]

        step = max(1, len(coords) // max_points)
        sampled = [coords[i] for i in range(0, len(coords), step)]
        # always include the last point
        if sampled[-1] != coords[-1]:
            sampled.append(coords[-1])
        return [(c[0], c[1]) for c in sampled[:max_points]]

    def _normalize_weather(self, data: dict) -> dict:
        """
        Extract weather features from an OpenWeatherMap response and
        compute a severity score between 0.0 (clear) and 1.0 (extreme).
        """
        main = data.get("main", {})
        wind = data.get("wind", {})
        weather_list = data.get("weather", [{}])
        weather_main = weather_list[0].get("main", "Clear") if weather_list else "Clear"
        weather_desc = weather_list[0].get("description", "") if weather_list else ""

        temp = main.get("temp", 293)  # Kelvin
        humidity = main.get("humidity", 50)
        wind_speed = wind.get("speed", 0)
        visibility = data.get("visibility", 10000)
        rain_1h = data.get("rain", {}).get("1h", 0)

        # Severity components (each 0-1)
        # Temperature extremes (below 0°C or above 40°C are dangerous)
        temp_c = temp - 273.15
        temp_severity = 0.0
        if temp_c < 0:
            temp_severity = min(abs(temp_c) / 20, 1.0)
        elif temp_c > 35:
            temp_severity = min((temp_c - 35) / 15, 1.0)

        wind_severity = min(wind_speed / 25, 1.0)  # 25 m/s = severe storm
        visibility_severity = max(0, 1.0 - (visibility / 10000))
        rain_severity = min(rain_1h / 20, 1.0)  # 20mm/h = very heavy rain
        humidity_severity = max(0, (humidity - 70) / 30) if humidity > 70 else 0.0

        # Condition-based boost
        condition_boost = 0.0
        severe_conditions = ["Thunderstorm", "Snow", "Tornado", "Squall"]
        moderate_conditions = ["Rain", "Drizzle", "Fog", "Mist", "Haze"]
        if weather_main in severe_conditions:
            condition_boost = 0.4
        elif weather_main in moderate_conditions:
            condition_boost = 0.15

        composite = (
            temp_severity * 0.15
            + wind_severity * 0.25
            + visibility_severity * 0.2
            + rain_severity * 0.25
            + humidity_severity * 0.05
            + condition_boost * 0.1
        )
        composite = min(composite + condition_boost * 0.5, 1.0)

        return {
            "temp_c": round(temp_c, 1),
            "humidity": humidity,
            "wind_speed": round(wind_speed, 1),
            "visibility": visibility,
            "rain_1h": rain_1h,
            "condition": weather_main,
            "description": weather_desc,
            "severity": round(composite, 4),
            "lat": data.get("coord", {}).get("lat"),
            "lon": data.get("coord", {}).get("lon"),
            "city_name": data.get("name", "Unknown"),
        }

    async def get_weather_at_point(self, lat: float, lon: float) -> dict:
        """Fetch weather for a single coordinate."""
        if not self.api_key or self.api_key == "your_api_key_here":
            # Return synthetic fallback data when no API key is configured
            return self._fallback_weather(lat, lon)

        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
        }
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(self.BASE_URL, params=params)
                resp.raise_for_status()
                return self._normalize_weather(resp.json())
        except Exception as e:
            print(f"Weather API error at ({lat},{lon}): {e}")
            return self._fallback_weather(lat, lon)

    def _fallback_weather(self, lat: float, lon: float) -> dict:
        """Generate plausible fallback weather when API is unavailable."""
        import random
        # Use coordinates as a seed for deterministic-ish but varied results
        seed = int(abs(lat * 100 + lon * 100)) % 100
        severity = round(random.Random(seed).uniform(0.1, 0.5), 4)
        return {
            "temp_c": round(25 + random.Random(seed).uniform(-5, 10), 1),
            "humidity": 60 + seed % 30,
            "wind_speed": round(random.Random(seed + 1).uniform(1, 12), 1),
            "visibility": 8000 + (seed * 20),
            "rain_1h": 0,
            "condition": "Clear",
            "description": "clear sky (fallback)",
            "severity": severity,
            "lat": lat,
            "lon": lon,
            "city_name": "Waypoint",
        }

    async def get_route_weather(
        self, route_coords: List[List[float]]
    ) -> Dict[str, Any]:
        """
        Given a list of [lat, lng] along a route, sample waypoints,
        fetch weather at each, and return aggregate + per-point data.
        """
        waypoints = self._sample_waypoints(route_coords, max_points=5)
        details = []
        for lat, lon in waypoints:
            point_weather = await self.get_weather_at_point(lat, lon)
            details.append(point_weather)

        if details:
            avg_severity = sum(d["severity"] for d in details) / len(details)
            max_severity = max(d["severity"] for d in details)
            # Use the higher of average and 70% of max to catch localized storms
            composite_severity = round(max(avg_severity, max_severity * 0.7), 4)
        else:
            composite_severity = 0.3  # default moderate

        # Build alerts for severe waypoints
        alerts = []
        for d in details:
            if d["severity"] > 0.6:
                alerts.append(
                    f"SEVERE: {d['condition']} at {d['city_name']} "
                    f"({d['lat']:.2f},{d['lon']:.2f}) — "
                    f"Wind: {d['wind_speed']}m/s, Rain: {d['rain_1h']}mm/h"
                )
            elif d["severity"] > 0.4:
                alerts.append(
                    f"WARNING: {d['condition']} at {d['city_name']} "
                    f"({d['lat']:.2f},{d['lon']:.2f})"
                )

        return {
            "severity": composite_severity,
            "waypoint_count": len(details),
            "details": details,
            "alerts": alerts,
        }
