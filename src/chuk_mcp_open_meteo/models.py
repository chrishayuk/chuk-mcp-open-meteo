"""Pydantic models for Open-Meteo API responses.

All API responses are properly typed using Pydantic models for type safety,
validation, and better IDE support.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


# Weather Forecast Models
class CurrentWeather(BaseModel):
    """Current weather conditions."""

    temperature: float = Field(..., description="Temperature in specified unit")
    windspeed: float = Field(..., description="Wind speed in specified unit")
    winddirection: float = Field(..., description="Wind direction in degrees")
    weathercode: int = Field(..., description="WMO weather code")
    time: str = Field(..., description="ISO 8601 timestamp")


class HourlyWeather(BaseModel):
    """Hourly weather forecast data."""

    model_config = ConfigDict(extra="allow")  # Allow additional fields from API

    time: list[str] = Field(..., description="ISO 8601 timestamps")
    temperature_2m: Optional[list[float]] = Field(None, description="Temperature at 2m height")
    relative_humidity_2m: Optional[list[float]] = Field(None, description="Relative humidity")
    precipitation: Optional[list[float]] = Field(None, description="Total precipitation")
    rain: Optional[list[float]] = Field(None, description="Rain")
    showers: Optional[list[float]] = Field(None, description="Showers")
    snowfall: Optional[list[float]] = Field(None, description="Snowfall")
    cloud_cover: Optional[list[float]] = Field(None, description="Cloud cover percentage")
    wind_speed_10m: Optional[list[float]] = Field(None, description="Wind speed at 10m")
    wind_direction_10m: Optional[list[float]] = Field(None, description="Wind direction")
    pressure_msl: Optional[list[float]] = Field(None, description="Pressure at sea level")


class DailyWeather(BaseModel):
    """Daily weather forecast data."""

    model_config = ConfigDict(extra="allow")  # Allow additional fields from API

    time: list[str] = Field(..., description="ISO 8601 dates")
    temperature_2m_max: Optional[list[float]] = Field(None, description="Maximum temperature")
    temperature_2m_min: Optional[list[float]] = Field(None, description="Minimum temperature")
    precipitation_sum: Optional[list[float]] = Field(None, description="Total precipitation")
    precipitation_hours: Optional[list[float]] = Field(None, description="Hours of precipitation")
    rain_sum: Optional[list[float]] = Field(None, description="Total rain")
    sunrise: Optional[list[str]] = Field(None, description="Sunrise time")
    sunset: Optional[list[str]] = Field(None, description="Sunset time")
    wind_speed_10m_max: Optional[list[float]] = Field(None, description="Maximum wind speed")


class WeatherForecast(BaseModel):
    """Complete weather forecast response."""

    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    elevation: Optional[float] = Field(None, description="Elevation in meters")
    timezone: Optional[str] = Field(None, description="Timezone name")
    timezone_abbreviation: Optional[str] = Field(None, description="Timezone abbreviation")
    current_weather: Optional[CurrentWeather] = Field(None, description="Current weather")
    hourly: Optional[HourlyWeather] = Field(None, description="Hourly forecast")
    daily: Optional[DailyWeather] = Field(None, description="Daily forecast")


# Geocoding Models
class GeocodingResult(BaseModel):
    """Single location result from geocoding."""

    id: Optional[int] = Field(None, description="Location ID")
    name: str = Field(..., description="Location name")
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")
    elevation: Optional[float] = Field(None, description="Elevation in meters")
    feature_code: Optional[str] = Field(None, description="GeoNames feature code")
    country_code: Optional[str] = Field(None, description="ISO 3166-1 alpha-2 country code")
    country: Optional[str] = Field(None, description="Country name")
    country_id: Optional[int] = Field(None, description="Country ID")
    timezone: Optional[str] = Field(None, description="Timezone name")
    population: Optional[int] = Field(None, description="Population")
    postcodes: Optional[list[str]] = Field(None, description="Postcodes")
    admin1: Optional[str] = Field(None, description="Administrative division level 1")
    admin2: Optional[str] = Field(None, description="Administrative division level 2")
    admin3: Optional[str] = Field(None, description="Administrative division level 3")
    admin4: Optional[str] = Field(None, description="Administrative division level 4")


class GeocodingResponse(BaseModel):
    """Geocoding API response."""

    results: Optional[list[GeocodingResult]] = Field(None, description="List of matching locations")
    generationtime_ms: Optional[float] = Field(None, description="Generation time in ms")


# Historical Weather (uses same models as forecast)
class HistoricalWeather(BaseModel):
    """Historical weather response."""

    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    elevation: Optional[float] = Field(None, description="Elevation in meters")
    timezone: Optional[str] = Field(None, description="Timezone name")
    timezone_abbreviation: Optional[str] = Field(None, description="Timezone abbreviation")
    hourly: Optional[HourlyWeather] = Field(None, description="Hourly historical data")
    daily: Optional[DailyWeather] = Field(None, description="Daily historical data")


# Air Quality Models
class HourlyAirQuality(BaseModel):
    """Hourly air quality data."""

    model_config = ConfigDict(extra="allow")  # Allow additional fields (pollen, etc.)

    time: list[str] = Field(..., description="ISO 8601 timestamps")
    pm10: Optional[list[Optional[float]]] = Field(None, description="PM10 in µg/m³")
    pm2_5: Optional[list[Optional[float]]] = Field(None, description="PM2.5 in µg/m³")
    carbon_monoxide: Optional[list[Optional[float]]] = Field(None, description="CO in µg/m³")
    nitrogen_dioxide: Optional[list[Optional[float]]] = Field(None, description="NO2 in µg/m³")
    sulphur_dioxide: Optional[list[Optional[float]]] = Field(None, description="SO2 in µg/m³")
    ozone: Optional[list[Optional[float]]] = Field(None, description="O3 in µg/m³")
    dust: Optional[list[Optional[float]]] = Field(None, description="Dust in µg/m³")
    uv_index: Optional[list[Optional[float]]] = Field(None, description="UV index")
    us_aqi: Optional[list[Optional[int]]] = Field(None, description="US AQI")
    european_aqi: Optional[list[Optional[int]]] = Field(None, description="European AQI")


class AirQualityResponse(BaseModel):
    """Air quality API response."""

    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    elevation: Optional[float] = Field(None, description="Elevation in meters")
    timezone: Optional[str] = Field(None, description="Timezone name")
    hourly: Optional[HourlyAirQuality] = Field(None, description="Hourly air quality data")


# Marine Forecast Models
class HourlyMarine(BaseModel):
    """Hourly marine forecast data."""

    model_config = ConfigDict(extra="allow")

    time: list[str] = Field(..., description="ISO 8601 timestamps")
    wave_height: Optional[list[Optional[float]]] = Field(
        None, description="Significant wave height in meters"
    )
    wave_direction: Optional[list[Optional[float]]] = Field(
        None, description="Wave direction in degrees"
    )
    wave_period: Optional[list[Optional[float]]] = Field(None, description="Wave period in seconds")
    wind_wave_height: Optional[list[Optional[float]]] = Field(
        None, description="Wind wave height in meters"
    )
    wind_wave_direction: Optional[list[Optional[float]]] = Field(
        None, description="Wind wave direction in degrees"
    )
    wind_wave_period: Optional[list[Optional[float]]] = Field(
        None, description="Wind wave period in seconds"
    )
    swell_wave_height: Optional[list[Optional[float]]] = Field(
        None, description="Swell wave height in meters"
    )
    swell_wave_direction: Optional[list[Optional[float]]] = Field(
        None, description="Swell wave direction in degrees"
    )
    swell_wave_period: Optional[list[Optional[float]]] = Field(
        None, description="Swell wave period in seconds"
    )
    ocean_current_velocity: Optional[list[Optional[float]]] = Field(
        None, description="Ocean current velocity in m/s"
    )
    ocean_current_direction: Optional[list[Optional[float]]] = Field(
        None, description="Ocean current direction in degrees"
    )


class DailyMarine(BaseModel):
    """Daily marine forecast data."""

    model_config = ConfigDict(extra="allow")

    time: list[str] = Field(..., description="ISO 8601 dates")
    wave_height_max: Optional[list[Optional[float]]] = Field(
        None, description="Maximum wave height"
    )
    wave_direction_dominant: Optional[list[Optional[float]]] = Field(
        None, description="Dominant wave direction"
    )
    wave_period_max: Optional[list[Optional[float]]] = Field(
        None, description="Maximum wave period"
    )


class MarineForecast(BaseModel):
    """Marine forecast API response."""

    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    elevation: Optional[float] = Field(None, description="Elevation in meters")
    timezone: Optional[str] = Field(None, description="Timezone name")
    hourly: Optional[HourlyMarine] = Field(None, description="Hourly marine forecast")
    daily: Optional[DailyMarine] = Field(None, description="Daily marine forecast")
