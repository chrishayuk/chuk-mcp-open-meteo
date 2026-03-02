"""Shared constants for the Open-Meteo MCP server."""

# API endpoints
FORECAST_API = "https://api.open-meteo.com/v1/forecast"
GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
HISTORICAL_API = "https://archive-api.open-meteo.com/v1/archive"
AIR_QUALITY_API = "https://air-quality-api.open-meteo.com/v1/air-quality"
MARINE_API = "https://marine-api.open-meteo.com/v1/marine"

# Default hourly variables (shared between single and batch tools)
DEFAULT_AIR_QUALITY_HOURLY = (
    "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,sulphur_dioxide,ozone,us_aqi,european_aqi"
)
DEFAULT_MARINE_HOURLY = (
    "wave_height,wave_direction,wave_period,wind_wave_height,swell_wave_height,sea_level_height_msl"
)

# WMO Weather Interpretation Codes (used by Open-Meteo)
WEATHER_CODES: dict[int, dict[str, str]] = {
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

# OpenWeatherMap icon CDN — maps severity categories to representative icon codes.
# Use @2x for high-DPI markers on maps.  "d" = day variant (always legible).
_OWM_CDN = "https://openweathermap.org/img/wn"

SEVERITY_ICONS: dict[str, str] = {
    "clear": f"{_OWM_CDN}/01d@2x.png",
    "cloudy": f"{_OWM_CDN}/04d@2x.png",
    "fog": f"{_OWM_CDN}/50d@2x.png",
    "drizzle": f"{_OWM_CDN}/09d@2x.png",
    "freezing": f"{_OWM_CDN}/13d@2x.png",
    "rain": f"{_OWM_CDN}/10d@2x.png",
    "snow": f"{_OWM_CDN}/13d@2x.png",
    "showers": f"{_OWM_CDN}/09d@2x.png",
    "thunderstorm": f"{_OWM_CDN}/11d@2x.png",
}
