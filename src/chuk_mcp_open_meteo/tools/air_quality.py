"""Air quality tools — single and batch."""

from typing import Any, Optional

import httpx
from chuk_mcp_server import tool

from .._batch import batch_fetch
from .._constants import AIR_QUALITY_API, DEFAULT_AIR_QUALITY_HOURLY
from ..models import (
    AirQualityResponse,
    BatchAirQualityItem,
    BatchAirQualityResponse,
)


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
        "hourly": hourly or DEFAULT_AIR_QUALITY_HOURLY,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(AIR_QUALITY_API, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    return AirQualityResponse(**data)


@tool
async def batch_get_air_quality(
    latitudes: str,
    longitudes: str,
    timezone: str = "auto",
    hourly: Optional[str] = None,
    domains: str = "auto",
) -> BatchAirQualityResponse:
    """Get air quality data for multiple locations in a single API call.

    This tool uses Open-Meteo's native batch support to fetch air quality data
    for many locations at once. Useful for comparing pollution levels across cities.

    Args:
        latitudes: Comma-separated latitude values for all locations.
            Example: "51.51,48.86,52.52"
            Must have the same number of values as longitudes.
        longitudes: Comma-separated longitude values for all locations.
            Example: "-0.13,2.35,13.41"
            Must have the same number of values as latitudes.
        timezone: Timezone name or "auto" for automatic detection per location
        hourly: Comma-separated air quality variables. If not provided, defaults to:
            pm10, pm2_5, carbon_monoxide, nitrogen_dioxide, sulphur_dioxide, ozone, us_aqi, european_aqi
        domains: Model domain - "auto" (default), "cams_global", "cams_europe"

    Returns:
        BatchAirQualityResponse: Contains:
            - results: List of BatchAirQualityItem, each with location_index and air_quality
            - total_locations: Number of locations queried

    Tips for LLMs:
        - Use batch_geocode_locations first to get coordinates
        - Results are in the SAME ORDER as the input coordinates
        - Useful for "compare air quality across cities" queries
        - All locations share the same hourly variables and domain settings

    Example:
        # Compare air quality across 3 cities
        result = await batch_get_air_quality(
            latitudes="51.51,48.86,34.05",
            longitudes="-0.13,2.35,-118.24",
            hourly="pm2_5,us_aqi"
        )
        for item in result.results:
            aqi = item.air_quality.hourly.us_aqi[0]
            print(f"Location {item.location_index}: AQI {aqi}")
    """
    params: dict[str, Any] = {
        "latitude": latitudes,
        "longitude": longitudes,
        "timezone": timezone,
        "domains": domains,
        "hourly": hourly or DEFAULT_AIR_QUALITY_HOURLY,
    }

    raw_items = await batch_fetch(AIR_QUALITY_API, params, AirQualityResponse)

    results = [
        BatchAirQualityItem(location_index=i, air_quality=item) for i, item in enumerate(raw_items)
    ]

    return BatchAirQualityResponse(
        results=results,
        total_locations=len(results),
    )
