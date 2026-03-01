"""Weather forecast tools — single and batch."""

from typing import Any, Optional

import httpx
from chuk_mcp_server import tool

from .._batch import batch_fetch
from .._constants import FORECAST_API
from ..models import (
    BatchWeatherForecastItem,
    BatchWeatherForecastResponse,
    WeatherForecast,
)


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
    """Get comprehensive weather forecast with current conditions, hourly, and daily forecasts.

    This tool provides detailed weather forecasts from Open-Meteo API with 50+ weather variables.
    Use this for answering questions about current weather, future forecasts, or detailed conditions.

    Args:
        latitude: Latitude coordinate in decimal degrees (-90 to 90). Use geocode_location to find coordinates.
        longitude: Longitude coordinate in decimal degrees (-180 to 180). Use geocode_location to find coordinates.
        temperature_unit: Temperature unit. Options: "celsius" (default), "fahrenheit"
        wind_speed_unit: Wind speed unit. Options: "kmh" (default), "ms", "mph", "kn"
        precipitation_unit: Precipitation unit. Options: "mm" (default), "inch"
        timezone: Timezone name (e.g., "America/New_York", "Europe/London") or "auto" for automatic detection
        forecast_days: Number of forecast days (1-16). Default is 7.
        current_weather: Set to True to include current weather conditions (recommended)
        hourly: Comma-separated list of hourly variables. Popular options:
            - temperature_2m: Temperature at 2m height
            - precipitation: Total precipitation (rain + snow)
            - rain: Rain only
            - snowfall: Snowfall amount
            - cloud_cover: Cloud cover percentage (0-100)
            - wind_speed_10m, wind_direction_10m: Wind at 10m height
            - relative_humidity_2m: Relative humidity
            - pressure_msl: Sea level pressure
            - visibility: Visibility distance
            - uv_index: UV index
        daily: Comma-separated list of daily variables. Popular options:
            - temperature_2m_max, temperature_2m_min: Daily temperature range
            - precipitation_sum: Total daily precipitation
            - rain_sum: Total daily rain
            - sunrise, sunset: Sun times
            - wind_speed_10m_max: Maximum daily wind speed
            - precipitation_hours: Hours with precipitation

    Returns:
        WeatherForecast: A Pydantic model containing:
            - latitude, longitude: Actual coordinates used
            - current_weather: Current conditions (temperature, wind, weather code)
            - hourly: Hourly forecast data (if requested)
            - daily: Daily forecast data (if requested)
            - timezone: Timezone information

    Tips for LLMs:
        - Always use current_weather=True for "what's the weather" questions
        - Request hourly data for detailed forecasts (e.g., "hourly rain predictions")
        - Request daily data for multi-day forecasts (e.g., "week ahead")
        - Weather codes: 0=clear, 1-3=partly cloudy, 45/48=fog, 51-57=drizzle, 61-67=rain, 71-77=snow, 80-82=rain showers, 95-99=thunderstorm

    Example:
        # Get current weather for London
        forecast = await get_weather_forecast(51.5072, -0.1276, current_weather=True)
        temp = forecast.current_weather.temperature

        # Get detailed 3-day forecast with hourly data
        forecast = await get_weather_forecast(
            51.5072, -0.1276,
            forecast_days=3,
            hourly="temperature_2m,precipitation,wind_speed_10m",
            daily="temperature_2m_max,temperature_2m_min,precipitation_sum"
        )
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
async def batch_get_weather_forecasts(
    latitudes: str,
    longitudes: str,
    temperature_unit: str = "celsius",
    wind_speed_unit: str = "kmh",
    precipitation_unit: str = "mm",
    timezone: str = "auto",
    forecast_days: int = 7,
    current_weather: bool = True,
    hourly: Optional[str] = None,
    daily: Optional[str] = None,
) -> BatchWeatherForecastResponse:
    """Get weather forecasts for multiple locations in a single API call.

    This tool uses Open-Meteo's native batch support to fetch forecasts for up to
    1000 locations in ONE HTTP request. This is dramatically faster than calling
    get_weather_forecast repeatedly.

    Use batch_geocode_locations first to get coordinates, then pass them here.

    Args:
        latitudes: Comma-separated latitude values for all locations.
            Example: "51.51,48.86,52.52" (London, Paris, Berlin)
            Must have the same number of values as longitudes.
        longitudes: Comma-separated longitude values for all locations.
            Example: "-0.13,2.35,13.41" (London, Paris, Berlin)
            Must have the same number of values as latitudes.
        temperature_unit: Temperature unit - "celsius" (default) or "fahrenheit"
        wind_speed_unit: Wind speed unit - "kmh" (default), "ms", "mph", "kn"
        precipitation_unit: Precipitation unit - "mm" (default) or "inch"
        timezone: Timezone name or "auto" for automatic detection per location
        forecast_days: Number of forecast days (1-16). Default is 7.
        current_weather: Include current weather conditions. Default is True.
        hourly: Comma-separated hourly variables (same as get_weather_forecast).
            Popular: temperature_2m, precipitation, wind_speed_10m, cloud_cover
        daily: Comma-separated daily variables (same as get_weather_forecast).
            Popular: temperature_2m_max, temperature_2m_min, precipitation_sum

    Returns:
        BatchWeatherForecastResponse: Contains:
            - results: List of BatchWeatherForecastItem, each with location_index and forecast
            - total_locations: Number of locations queried

    Tips for LLMs:
        - ALWAYS use batch_geocode_locations first to get coordinates
        - The forecasts are returned in the SAME ORDER as the input coordinates
        - All locations share the same forecast parameters (hourly, daily, units)
        - For different parameters per location, make separate get_weather_forecast calls
        - Maximum ~1000 locations per call (Open-Meteo API limit)
        - The latitudes and longitudes strings must have equal numbers of comma-separated values

    Workflow for "What's the weather across the UK?":
        1. batch_geocode_locations("London,Manchester,Edinburgh,Cardiff,Belfast,Birmingham")
        2. Extract latitudes and longitudes from successful results
        3. batch_get_weather_forecasts(latitudes="51.51,53.48,55.95,...", longitudes="-0.13,-2.24,-3.19,...")
        4. Present the weather comparison to the user

    Example:
        # Get weather for London, Paris, and Berlin
        forecasts = await batch_get_weather_forecasts(
            latitudes="51.51,48.86,52.52",
            longitudes="-0.13,2.35,13.41",
            current_weather=True,
            daily="temperature_2m_max,temperature_2m_min,precipitation_sum"
        )
        for item in forecasts.results:
            f = item.forecast
            print(f"Location {item.location_index}: {f.current_weather.temperature}C")
    """
    params: dict[str, Any] = {
        "latitude": latitudes,
        "longitude": longitudes,
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

    raw_items = await batch_fetch(FORECAST_API, params, WeatherForecast)

    results = [
        BatchWeatherForecastItem(location_index=i, forecast=item)
        for i, item in enumerate(raw_items)
    ]

    return BatchWeatherForecastResponse(
        results=results,
        total_locations=len(results),
    )
