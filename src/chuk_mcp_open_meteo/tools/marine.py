"""Marine forecast tools — single and batch."""

from typing import Any, Optional

import httpx
from chuk_mcp_server import tool

from .._batch import batch_fetch
from .._constants import DEFAULT_MARINE_HOURLY, MARINE_API
from ..models import (
    BatchMarineForecastItem,
    BatchMarineForecastResponse,
    MarineForecast,
)


@tool
async def get_marine_forecast(
    latitude: float,
    longitude: float,
    timezone: str = "auto",
    hourly: Optional[str] = None,
    daily: Optional[str] = None,
    forecast_days: int = 7,
) -> MarineForecast:
    """Get ocean and marine weather forecasts including waves, swell, currents, and TIDES.

    **PRIMARY USE FOR TIDES**: This tool provides tidal height predictions via the 'sea_level_height_msl' variable.
    Use this when users ask about tide times, high/low tides, or tide heights for coastal locations.

    Also use this for maritime activities, surfing, sailing, fishing, or beach conditions.
    Provides detailed wave forecasts from multiple global ocean models.

    Args:
        latitude: Latitude coordinate in decimal degrees (-90 to 90). Must be over ocean/coastal areas.
            Use geocode_location to find coordinates for coastal cities and beaches.
        longitude: Longitude coordinate in decimal degrees (-180 to 180). Must be over ocean/coastal areas.
        timezone: Timezone name (e.g., "Pacific/Auckland", "Europe/London") or "auto" for automatic
        hourly: Comma-separated list of hourly marine variables. Popular options:
            Wave characteristics (total):
            - wave_height: Significant wave height in meters (combined wind + swell)
            - wave_direction: Wave direction in degrees (0-360, meteorological convention)
            - wave_period: Wave period in seconds

            Wind waves (locally generated):
            - wind_wave_height: Wind wave height in meters
            - wind_wave_direction: Wind wave direction in degrees
            - wind_wave_period: Wind wave period in seconds
            - wind_wave_peak_period: Peak period of wind waves

            Swell waves (distant storms):
            - swell_wave_height: Swell wave height in meters
            - swell_wave_direction: Swell wave direction in degrees
            - swell_wave_period: Swell wave period in seconds
            - swell_wave_peak_period: Peak period of swell

            Ocean currents:
            - ocean_current_velocity: Current speed in m/s
            - ocean_current_direction: Current direction in degrees

            Tides (IMPORTANT for tide predictions):
            - sea_level_height_msl: Sea level height in meters (includes tides - shows clear tidal cycles)

            Other useful variables:
            - sea_surface_temperature: Water temperature in °C

            NOTE: Do NOT include regular weather variables like 'wind_speed', 'temperature',
            'precipitation' - those come from get_weather_forecast, not marine API!

        daily: Comma-separated list of daily marine variables. Options:
            - wave_height_max: Maximum wave height for the day
            - wave_direction_dominant: Dominant wave direction
            - wave_period_max: Maximum wave period
        forecast_days: Number of forecast days (1-16). Default is 7.

    Returns:
        MarineForecast: A Pydantic model containing:
            - latitude, longitude: Actual coordinates used (may be adjusted to nearest ocean grid point)
            - hourly: Hourly marine forecast data (wave heights, directions, periods, currents)
            - daily: Daily marine forecast data (if requested)
            - timezone: Timezone information

    Tips for LLMs:
        - **TIDE QUERIES**: When user asks "what are the tide times" or "when is high/low tide":
            1. Use geocode_location to get coordinates (try just city name if "City, Region" fails)
            2. Call this tool with hourly="sea_level_height_msl" immediately (don't ask for clarification first!)
            3. Analyze the sea_level_height_msl values to find peaks (high tide) and troughs (low tide)
            4. Present the times and heights to the user
            Example: "High tide at 05:00 (+1.63m), Low tide at 12:00 (-2.17m)"
        - Use this for surfing, sailing, boating, fishing, beach safety questions
        - wave_height is the key metric - measured in meters:
            * 0-0.5m: Calm, good for swimming
            * 0.5-1.5m: Small waves, beginner surfing
            * 1.5-2.5m: Moderate waves, intermediate surfing
            * 2.5-4m: Large waves, advanced surfing
            * 4m+: Very large, dangerous for most activities
        - wave_period (seconds) indicates wave quality for surfing:
            * <8s: Short period, choppy (wind waves)
            * 8-12s: Medium period, good surf
            * 12s+: Long period, excellent surf (swell)
        - Combine with get_weather_forecast for complete marine conditions (wind, visibility, storms)
        - For surfing: need wave_height (size), wave_period (quality), and local wind (from weather forecast)
        - swell_wave data shows waves from distant storms (clean, organized)
        - wind_wave data shows local wind-generated waves (choppy if strong winds)
        - ocean_current data important for safety and navigation

    Common use cases:
        - **Tide predictions**: Use sea_level_height_msl to find high/low tide times and heights
        - Surfing: Check wave_height, wave_period, swell_wave_height, and sea_level_height_msl (tides affect wave quality)
        - Swimming safety: Check wave_height (stay <1m for safety) and sea_level_height_msl (avoid swimming during strong tidal currents)
        - Sailing/boating: Check wave_height, wave_period, ocean_current_velocity, and sea_level_height_msl (for harbor entry/exit timing)
        - Fishing: Check ocean_current, sea_surface_temperature, and sea_level_height_msl (fish feeding patterns follow tides)
        - Beach conditions: Check wave_height, sea_level_height_msl, and combine with weather forecast (wind, rain)

    Example:
        # Get tide times and heights for a coastal location
        marine = await get_marine_forecast(
            51.5074, -0.1278,  # Example coordinates (coastal UK)
            hourly="sea_level_height_msl",
            timezone="Europe/London",
            forecast_days=1
        )
        # Find high and low tides by analyzing sea_level_height_msl values
        # High tide = maximum values (e.g., +1.5m), Low tide = minimum values (e.g., -2.0m)
        # Tidal cycle repeats approximately every 12 hours (two highs and two lows per day)

        # Get surf conditions for Hawaii (including tides)
        marine = await get_marine_forecast(
            21.3099, -157.8581,  # Honolulu coordinates
            hourly="wave_height,wave_period,swell_wave_height,swell_wave_direction,sea_level_height_msl",
            forecast_days=3
        )
        current_wave_height = marine.hourly.wave_height[0]
        current_period = marine.hourly.wave_period[0]
        current_tide = marine.hourly.sea_level_height_msl[0]

        # Check if good for surfing
        if 1.5 <= current_wave_height <= 3.0 and current_period >= 10:
            print("Good surf conditions!")

        # Get daily max waves for trip planning
        marine = await get_marine_forecast(
            lat, lon,
            daily="wave_height_max,wave_direction_dominant",
            forecast_days=7
        )
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "forecast_days": forecast_days,
        "hourly": hourly or DEFAULT_MARINE_HOURLY,
    }

    if daily:
        params["daily"] = daily

    async with httpx.AsyncClient() as client:
        response = await client.get(MARINE_API, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    return MarineForecast(**data)


@tool
async def batch_get_marine_forecasts(
    latitudes: str,
    longitudes: str,
    timezone: str = "auto",
    hourly: Optional[str] = None,
    daily: Optional[str] = None,
    forecast_days: int = 7,
) -> BatchMarineForecastResponse:
    """Get marine forecasts for multiple coastal locations in a single API call.

    This tool uses Open-Meteo's native batch support to fetch marine conditions
    for many locations at once. Useful for comparing surf spots, planning coastal
    trips, or monitoring conditions along a coastline.

    Args:
        latitudes: Comma-separated latitude values for all locations.
            Example: "21.31,33.87,36.97" (Honolulu, San Diego, Monterey)
            Must be over ocean/coastal areas. Same count as longitudes.
        longitudes: Comma-separated longitude values for all locations.
            Example: "-157.86,-118.29,-122.00"
            Must be over ocean/coastal areas. Same count as latitudes.
        timezone: Timezone name or "auto" for automatic detection per location
        hourly: Comma-separated hourly marine variables. If not provided, defaults to:
            wave_height, wave_direction, wave_period, wind_wave_height, swell_wave_height, sea_level_height_msl
        daily: Comma-separated daily marine variables (e.g., wave_height_max, wave_direction_dominant)
        forecast_days: Number of forecast days (1-16). Default is 7.

    Returns:
        BatchMarineForecastResponse: Contains:
            - results: List of BatchMarineForecastItem, each with location_index and forecast
            - total_locations: Number of locations queried

    Tips for LLMs:
        - Use batch_geocode_locations first to get coordinates for coastal cities
        - Results are in the SAME ORDER as the input coordinates
        - Useful for "compare surf conditions" or "wave heights along the coast" queries
        - All locations share the same hourly/daily variables and forecast_days
        - Coordinates must be over ocean/coastal areas (inland locations will fail)

    Example:
        # Compare surf conditions at 3 beaches
        result = await batch_get_marine_forecasts(
            latitudes="21.31,33.87,36.97",
            longitudes="-157.86,-118.29,-122.00",
            hourly="wave_height,wave_period,swell_wave_height",
            forecast_days=3
        )
        for item in result.results:
            waves = item.forecast.hourly.wave_height[0]
            print(f"Location {item.location_index}: {waves}m waves")
    """
    params: dict[str, Any] = {
        "latitude": latitudes,
        "longitude": longitudes,
        "timezone": timezone,
        "forecast_days": forecast_days,
        "hourly": hourly or DEFAULT_MARINE_HOURLY,
    }

    if daily:
        params["daily"] = daily

    raw_items = await batch_fetch(MARINE_API, params, MarineForecast)

    results = [
        BatchMarineForecastItem(location_index=i, forecast=item) for i, item in enumerate(raw_items)
    ]

    return BatchMarineForecastResponse(
        results=results,
        total_locations=len(results),
    )
