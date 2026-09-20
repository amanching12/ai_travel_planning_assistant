import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Singapore Weather Server")


@mcp.tool(description="Get current weather and a daily forecast for a city.")
def get_weather_forecast(city: str = "Singapore", days: int = 3) -> dict:
    days = max(1, min(int(days), 7))
    geo = httpx.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "en", "format": "json"},
        timeout=15,
    )
    geo.raise_for_status()
    results = geo.json().get("results", [])
    if not results:
        return {"error": f"City not found: {city}"}

    place = results[0]
    latitude = place["latitude"]
    longitude = place["longitude"]

    forecast = httpx.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code",
            "forecast_days": days,
            "timezone": "auto",
        },
        timeout=15,
    )
    forecast.raise_for_status()
    data = forecast.json()
    return {
        "city": place.get("name", city),
        "country": place.get("country", ""),
        "latitude": latitude,
        "longitude": longitude,
        "current": data.get("current", {}),
        "daily": data.get("daily", {}),
        "source": "Open-Meteo weather and geocoding APIs",
    }


if __name__ == "__main__":
    mcp.run()
