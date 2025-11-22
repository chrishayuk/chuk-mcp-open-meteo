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
    WeatherCodeInterpretation,
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

# WMO Weather Interpretation Codes (used by Open-Meteo)
WEATHER_CODES = {
    0: {"description": "Clear sky", "severity": "clear"},
    1: {"description": "Mainly clear", "severity": "clear"},
    2: {"description": "Partly cloudy", "severity": "cloudy"},
    3: {"description": "Overcast", "severity": "cloudy"},
    45: {"description": "Fog", "severity": "fog"},
    48: {"description": "Depositing rime fog", "severity": "fog"},
    51: {"description": "Light drizzle", "severity": "drizzle"},
    53: {"description": "Moderate drizzle", "severity": "drizzle"},
    55: {"description": "Dense drizzle", "severity": "drizzle"},
    56: {"description": "Light freezing drizzle", "severity": "freezing"},
    57: {"description": "Dense freezing drizzle", "severity": "freezing"},
    61: {"description": "Slight rain", "severity": "rain"},
    63: {"description": "Moderate rain", "severity": "rain"},
    65: {"description": "Heavy rain", "severity": "rain"},
    66: {"description": "Light freezing rain", "severity": "freezing"},
    67: {"description": "Heavy freezing rain", "severity": "freezing"},
    71: {"description": "Slight snow fall", "severity": "snow"},
    73: {"description": "Moderate snow fall", "severity": "snow"},
    75: {"description": "Heavy snow fall", "severity": "snow"},
    77: {"description": "Snow grains", "severity": "snow"},
    80: {"description": "Slight rain showers", "severity": "showers"},
    81: {"description": "Moderate rain showers", "severity": "showers"},
    82: {"description": "Violent rain showers", "severity": "showers"},
    85: {"description": "Slight snow showers", "severity": "snow"},
    86: {"description": "Heavy snow showers", "severity": "snow"},
    95: {"description": "Thunderstorm", "severity": "thunderstorm"},
    96: {"description": "Thunderstorm with slight hail", "severity": "thunderstorm"},
    99: {"description": "Thunderstorm with heavy hail", "severity": "thunderstorm"},
}


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
async def geocode_location(
    name: str,
    count: int = 10,
    language: str = "en",
    format: str = "json",
) -> GeocodingResponse:
    """Convert location names to coordinates and get detailed geographic information.

    Use this tool FIRST before calling weather tools to get accurate coordinates for any location.
    Searches worldwide database of cities, towns, and places with comprehensive metadata.

    Args:
        name: Location name to search for. Can be:
            - City name: "London", "Tokyo", "New York"
            - City with country: "Paris, France", "Portland, Oregon"
            - Region or landmark: "Cornwall", "Lake Tahoe"
            - Address or place: "Times Square", "Big Ben"
        count: Maximum number of results to return (1-100). Default is 10.
            Use 1 if you're confident about the location (e.g., "London, UK")
            Use 5-10 for ambiguous names (e.g., "Paris" - could be France, Texas, etc.)
        language: Language code for result names. Options: "en" (English, default), "de" (German),
            "fr" (French), "es" (Spanish), "it" (Italian), "pt" (Portuguese), etc.
        format: Response format. Always use "json" (default).

    Returns:
        GeocodingResponse: A Pydantic model containing:
            - results: List of matching locations, each with:
                - name: Location name
                - latitude, longitude: Coordinates (use these for weather tools!)
                - country, country_code: Country information
                - timezone: IANA timezone (e.g., "Europe/London")
                - elevation: Meters above sea level
                - population: Population (if available)
                - admin1, admin2: Administrative divisions (state, county, etc.)
                - feature_code: Type of place (PPLC=capital, PPL=populated place, etc.)

    Tips for LLMs:
        - ALWAYS geocode location names before requesting weather data
        - Results are sorted by relevance (population, importance)
        - First result is usually what users mean for well-known cities
        - For ambiguous names, check country/admin divisions to pick the right one
        - Use the exact latitude/longitude from results in weather API calls
        - Timezone from geocoding can be passed to weather APIs for local time
        - **CRITICAL**: If no results found, IMMEDIATELY retry with simpler search terms!
          The API works best with just city names (e.g., "Portland" not "Portland Harbor" or "Portland, Maine")
          WORKFLOW: If "City, Region" fails → AUTOMATICALLY try just "City" → filter by admin1/admin2/country
          DO NOT ask the user - just retry automatically with the simpler name!
        - If still no results after retry: try even simpler terms or use nearest known location
        - Common pattern: "Harbor Name" fails → retry just the city name → filter by region/country

    Example:
        # Find London coordinates
        locations = await geocode_location("London", count=1)
        london = locations.results[0]
        # Use coordinates for weather: london.latitude, london.longitude

        # Handle ambiguous names
        locations = await geocode_location("Paris", count=5)
        # results[0] = Paris, France (population 2.1M)
        # results[1] = Paris, Texas (population 25K)
        # Pick based on context or ask user

        # If "City, Region" returns no results, try just "City"
        locations = await geocode_location("Portland, Maine", count=5)
        if not locations.results:
            # Try simpler search
            locations = await geocode_location("Portland", count=5)
            # Filter by country_code='US' and admin1='Maine' to get the right one
            portland = next(r for r in locations.results if r.country_code == 'US' and r.admin1 == 'Maine')
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
    }

    if hourly:
        params["hourly"] = hourly
    else:
        # Default to key marine metrics including tides
        params["hourly"] = (
            "wave_height,wave_direction,wave_period,wind_wave_height,swell_wave_height,sea_level_height_msl"
        )

    if daily:
        params["daily"] = daily

    async with httpx.AsyncClient() as client:
        response = await client.get(MARINE_API, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    return MarineForecast(**data)


@tool
async def interpret_weather_code(weather_code: int) -> WeatherCodeInterpretation:
    """Interpret WMO weather codes used by Open-Meteo API.

    Weather codes are numerical values (0-99) that represent different weather conditions.
    This tool translates codes into human-readable descriptions.

    Args:
        weather_code: WMO weather code integer (0-99) from weather forecast data.
            This is the 'weathercode' field in current_weather or hourly/daily data.

    Returns:
        WeatherCodeInterpretation: Pydantic model with:
            - code: The weather code number
            - description: Human-readable weather condition
            - severity: Category (clear, cloudy, fog, drizzle, rain, freezing, snow, showers, thunderstorm)

    Common Weather Codes:
        Clear/Cloudy (0-3):
            0 = Clear sky
            1 = Mainly clear
            2 = Partly cloudy
            3 = Overcast

        Fog (45-48):
            45 = Fog
            48 = Depositing rime fog

        Drizzle (51-57):
            51 = Light drizzle
            53 = Moderate drizzle
            55 = Dense drizzle
            56-57 = Freezing drizzle

        Rain (61-67):
            61 = Slight rain
            63 = Moderate rain
            65 = Heavy rain
            66-67 = Freezing rain

        Snow (71-77, 85-86):
            71 = Slight snow
            73 = Moderate snow
            75 = Heavy snow
            77 = Snow grains
            85-86 = Snow showers

        Showers (80-82):
            80 = Slight rain showers
            81 = Moderate rain showers
            82 = Violent rain showers

        Thunderstorm (95-99):
            95 = Thunderstorm
            96 = Thunderstorm with slight hail
            99 = Thunderstorm with heavy hail

    Tips for LLMs:
        - Use this to explain weather conditions to users in natural language
        - Severity helps determine appropriate activity recommendations
        - Codes 0-3: Generally safe outdoor conditions
        - Codes 51-65: Wet conditions, bring umbrella
        - Codes 71-77: Snow conditions, winter gear needed
        - Codes 80-99: Severe weather, take precautions
        - Unknown codes return "Unknown weather code" - may be API error

    Example:
        # Get weather and interpret code
        forecast = await get_weather_forecast(lat, lon, current_weather=True)
        code = forecast.current_weather.weathercode
        interpretation = await interpret_weather_code(code)
        # Returns: WeatherCodeInterpretation(code=61, description="Slight rain", severity="rain")
    """
    if weather_code in WEATHER_CODES:
        return WeatherCodeInterpretation(
            code=weather_code,
            description=WEATHER_CODES[weather_code]["description"],
            severity=WEATHER_CODES[weather_code]["severity"],
        )
    else:
        return WeatherCodeInterpretation(
            code=weather_code,
            description=f"Unknown weather code: {weather_code}",
            severity="unknown",
        )


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
