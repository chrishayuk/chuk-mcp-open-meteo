"""Open-Meteo MCP Server - The best weather MCP server ever.

Provides comprehensive weather data through multiple tools:
- Weather forecasts (current, hourly, daily)
- Location geocoding
- Historical weather data
- Air quality information
- Marine weather forecasts

All responses use Pydantic models for type safety and validation.
"""

import logging
import sys
from typing import Optional

import httpx
from chuk_mcp_server import run, tool

from .models import (
    AirQualityResponse,
    GeocodingResponse,
    HistoricalWeather,
    MarineForecast,
    WeatherForecast,
)

# Configure logging
# In STDIO mode, we need to be quiet to avoid polluting the JSON-RPC stream
# Only log to stderr, and only warnings/errors
logging.basicConfig(
    level=logging.WARNING, format="%(levelname)s:%(name)s:%(message)s", stream=sys.stderr
)
logger = logging.getLogger(__name__)

# Constants
FORECAST_API = "https://api.open-meteo.com/v1/forecast"
GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
HISTORICAL_API = "https://archive-api.open-meteo.com/v1/archive"
AIR_QUALITY_API = "https://air-quality-api.open-meteo.com/v1/air-quality"
MARINE_API = "https://marine-api.open-meteo.com/v1/marine"


@tool
async def get_weather_forecast(
    latitude: float,
    longitude: float,
    temperature_unit: str = "celsius",
    wind_speed_unit: str = "kmh",
    precipitation_unit: str = "mm",
    timezone: str = "auto",
    forecast_days: int = 7,
    current_weather: bool = True,
    hourly: Optional[str] = None,
    daily: Optional[str] = None,
) -> WeatherForecast:
    """Get comprehensive weather forecast from Open-Meteo API.

    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
        temperature_unit: Temperature unit - celsius, fahrenheit
        wind_speed_unit: Wind speed unit - kmh, ms, mph, kn
        precipitation_unit: Precipitation unit - mm, inch
        timezone: Timezone (e.g., 'America/New_York', 'auto' for automatic)
        forecast_days: Number of forecast days (1-16)
        current_weather: Include current weather conditions
        hourly: Comma-separated hourly variables (e.g., 'temperature_2m,precipitation')
        daily: Comma-separated daily variables (e.g., 'temperature_2m_max,precipitation_sum')

    Returns:
        WeatherForecast: Pydantic model with forecast data

    Example:
        forecast = await get_weather_forecast(51.5072, -0.1276, current_weather=True)
        print(f"Temperature: {forecast.current_weather.temperature}°C")
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "temperature_unit": temperature_unit,
        "wind_speed_unit": wind_speed_unit,
        "precipitation_unit": precipitation_unit,
        "timezone": timezone,
        "forecast_days": forecast_days,
    }

    if current_weather:
        params["current_weather"] = "true"

    if hourly:
        params["hourly"] = hourly

    if daily:
        params["daily"] = daily

    async with httpx.AsyncClient() as client:
        response = await client.get(FORECAST_API, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    return WeatherForecast(**data)


@tool
async def geocode_location(
    name: str,
    count: int = 10,
    language: str = "en",
    format: str = "json",
) -> GeocodingResponse:
    """Search for locations and get their coordinates using Open-Meteo Geocoding API.

    Args:
        name: Location name to search for (e.g., 'London', 'New York')
        count: Number of results to return (1-100)
        language: Language code for results (en, de, fr, es, etc.)
        format: Response format (json)

    Returns:
        GeocodingResponse: Pydantic model with location results

    Example:
        locations = await geocode_location("Paris", count=3)
        for loc in locations.results:
            print(f"{loc.name}, {loc.country}: {loc.latitude}, {loc.longitude}")
    """
    params = {
        "name": name,
        "count": count,
        "language": language,
        "format": format,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(GEOCODING_API, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    return GeocodingResponse(**data)


@tool
async def get_historical_weather(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    temperature_unit: str = "celsius",
    wind_speed_unit: str = "kmh",
    precipitation_unit: str = "mm",
    timezone: str = "auto",
    hourly: Optional[str] = None,
    daily: Optional[str] = None,
) -> HistoricalWeather:
    """Get historical weather data from Open-Meteo Archive API.

    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        temperature_unit: Temperature unit - celsius, fahrenheit
        wind_speed_unit: Wind speed unit - kmh, ms, mph, kn
        precipitation_unit: Precipitation unit - mm, inch
        timezone: Timezone (e.g., 'America/New_York', 'auto' for automatic)
        hourly: Comma-separated hourly variables
        daily: Comma-separated daily variables

    Returns:
        HistoricalWeather: Pydantic model with historical data

    Example:
        historical = await get_historical_weather(
            48.8566, 2.3522,
            "2024-01-01", "2024-01-07",
            daily="temperature_2m_max,temperature_2m_min"
        )
        avg_high = sum(historical.daily.temperature_2m_max) / len(historical.daily.temperature_2m_max)
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date,
        "end_date": end_date,
        "temperature_unit": temperature_unit,
        "wind_speed_unit": wind_speed_unit,
        "precipitation_unit": precipitation_unit,
        "timezone": timezone,
    }

    if hourly:
        params["hourly"] = hourly

    if daily:
        params["daily"] = daily

    async with httpx.AsyncClient() as client:
        response = await client.get(HISTORICAL_API, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    return HistoricalWeather(**data)


@tool
async def get_air_quality(
    latitude: float,
    longitude: float,
    timezone: str = "auto",
    hourly: Optional[str] = None,
    domains: str = "auto",
) -> AirQualityResponse:
    """Get air quality data and forecasts from Open-Meteo Air Quality API.

    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
        timezone: Timezone (e.g., 'America/New_York', 'auto' for automatic)
        hourly: Comma-separated air quality variables
        domains: Model domain - auto, cams_global, cams_europe

    Returns:
        AirQualityResponse: Pydantic model with air quality data

    Example:
        air = await get_air_quality(34.0522, -118.2437)
        if air.hourly and air.hourly.us_aqi:
            aqi = air.hourly.us_aqi[0]
            print(f"US AQI: {aqi}")
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "domains": domains,
    }

    if hourly:
        params["hourly"] = hourly
    else:
        # Default to common air quality metrics
        params["hourly"] = (
            "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi,european_aqi"
        )

    async with httpx.AsyncClient() as client:
        response = await client.get(AIR_QUALITY_API, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    return AirQualityResponse(**data)


@tool
async def get_marine_forecast(
    latitude: float,
    longitude: float,
    timezone: str = "auto",
    hourly: Optional[str] = None,
    daily: Optional[str] = None,
    forecast_days: int = 7,
) -> MarineForecast:
    """Get marine weather forecast from Open-Meteo Marine API.

    Args:
        latitude: Latitude coordinate (-90 to 90)
        longitude: Longitude coordinate (-180 to 180)
        timezone: Timezone (e.g., 'America/New_York', 'auto' for automatic)
        hourly: Comma-separated marine variables
        daily: Comma-separated daily marine variables
        forecast_days: Number of forecast days (1-16)

    Returns:
        MarineForecast: Pydantic model with marine forecast data

    Example:
        marine = await get_marine_forecast(21.3099, -157.8581)
        if marine.hourly and marine.hourly.wave_height:
            height = marine.hourly.wave_height[0]
            print(f"Wave height: {height}m")
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "forecast_days": forecast_days,
    }

    if hourly:
        params["hourly"] = hourly
    else:
        # Default to key marine metrics
        params["hourly"] = (
            "wave_height,wave_direction,wave_period,wind_wave_height,swell_wave_height"
        )

    if daily:
        params["daily"] = daily

    async with httpx.AsyncClient() as client:
        response = await client.get(MARINE_API, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    return MarineForecast(**data)


def main():
    """Run the Open-Meteo MCP server."""
    # Check if transport is specified in command line args
    # Default to stdio for MCP compatibility (Claude Desktop, mcp-cli)
    transport = "stdio"

    # Allow HTTP mode via command line
    if len(sys.argv) > 1 and sys.argv[1] in ["http", "--http"]:
        transport = "http"
        # Only log in HTTP mode
        logger.warning("Starting Chuk MCP Open-Meteo Server in HTTP mode")

    # Suppress chuk_mcp_server logging in STDIO mode
    if transport == "stdio":
        # Set chuk_mcp_server loggers to ERROR only
        logging.getLogger("chuk_mcp_server").setLevel(logging.ERROR)
        logging.getLogger("chuk_mcp_server.core").setLevel(logging.ERROR)
        logging.getLogger("chuk_mcp_server.stdio_transport").setLevel(logging.ERROR)
        # Suppress httpx logging (API calls)
        logging.getLogger("httpx").setLevel(logging.ERROR)

    run(transport=transport)


if __name__ == "__main__":
    main()
