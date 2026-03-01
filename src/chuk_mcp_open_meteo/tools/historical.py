"""Historical weather tools — single and batch."""

from typing import Any, Optional

import httpx
from chuk_mcp_server import tool

from .._batch import batch_fetch
from .._constants import HISTORICAL_API
from ..models import (
    BatchHistoricalWeatherItem,
    BatchHistoricalWeatherResponse,
    HistoricalWeather,
)


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
async def batch_get_historical_weather(
    latitudes: str,
    longitudes: str,
    start_date: str,
    end_date: str,
    temperature_unit: str = "celsius",
    wind_speed_unit: str = "kmh",
    precipitation_unit: str = "mm",
    timezone: str = "auto",
    hourly: Optional[str] = None,
    daily: Optional[str] = None,
) -> BatchHistoricalWeatherResponse:
    """Get historical weather data for multiple locations in a single API call.

    This tool uses Open-Meteo's native batch support to fetch historical weather
    for many locations at once. All locations share the same date range.

    Args:
        latitudes: Comma-separated latitude values for all locations.
            Example: "51.51,48.86,52.52"
            Must have the same number of values as longitudes.
        longitudes: Comma-separated longitude values for all locations.
            Example: "-0.13,2.35,13.41"
            Must have the same number of values as latitudes.
        start_date: Start date in YYYY-MM-DD format (shared across all locations)
        end_date: End date in YYYY-MM-DD format (shared across all locations)
        temperature_unit: Temperature unit - "celsius" (default) or "fahrenheit"
        wind_speed_unit: Wind speed unit - "kmh" (default), "ms", "mph", "kn"
        precipitation_unit: Precipitation unit - "mm" (default) or "inch"
        timezone: Timezone name or "auto" for automatic detection per location
        hourly: Comma-separated hourly variables (same as get_historical_weather).
        daily: Comma-separated daily variables (same as get_historical_weather).

    Returns:
        BatchHistoricalWeatherResponse: Contains:
            - results: List of BatchHistoricalWeatherItem, each with location_index and weather
            - total_locations: Number of locations queried

    Tips for LLMs:
        - Use batch_geocode_locations first to get coordinates
        - All locations share the same date range - if you need different dates per location,
          use separate get_historical_weather calls
        - Results are in the SAME ORDER as the input coordinates
        - Useful for climate comparisons across cities for the same time period

    Example:
        # Compare last week's weather across European capitals
        result = await batch_get_historical_weather(
            latitudes="51.51,48.86,52.52",
            longitudes="-0.13,2.35,13.41",
            start_date="2025-01-01",
            end_date="2025-01-07",
            daily="temperature_2m_max,temperature_2m_min,precipitation_sum"
        )
    """
    params: dict[str, Any] = {
        "latitude": latitudes,
        "longitude": longitudes,
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

    raw_items = await batch_fetch(HISTORICAL_API, params, HistoricalWeather)

    results = [
        BatchHistoricalWeatherItem(location_index=i, weather=item)
        for i, item in enumerate(raw_items)
    ]

    return BatchHistoricalWeatherResponse(
        results=results,
        total_locations=len(results),
    )
