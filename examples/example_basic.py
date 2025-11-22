#!/usr/bin/env python3
"""Basic example of using the Open-Meteo MCP server tools directly.

This script demonstrates how to call the weather tools programmatically
without going through the MCP protocol. All tools return Pydantic models
for type-safe access.
"""

import asyncio
from chuk_mcp_open_meteo.server import (
    get_weather_forecast,
    geocode_location,
    get_historical_weather,
    get_air_quality,
    get_marine_forecast,
)


async def main():
    """Run basic examples of each tool."""

    print("=" * 80)
    print("BASIC WEATHER TOOL EXAMPLES")
    print("=" * 80)
    print()

    # Example 1: Get current weather for London
    print("1. Current Weather in London")
    print("-" * 80)
    london_weather = await get_weather_forecast(
        latitude=51.5072,
        longitude=-0.1276,
        current_weather=True,
    )

    if london_weather.current_weather:
        current = london_weather.current_weather
        print(f"Temperature: {current.temperature}°C")
        print(f"Wind Speed: {current.windspeed} km/h")
        print(f"Wind Direction: {current.winddirection}°")
        print(f"Weather Code: {current.weathercode}")
    print()

    # Example 2: Geocode a location
    print("2. Geocoding 'Paris'")
    print("-" * 80)
    paris_results = await geocode_location(name="Paris", count=3)

    if paris_results.results:
        for i, location in enumerate(paris_results.results[:3], 1):
            print(f"{i}. {location.name}, {location.country}")
            print(f"   Coordinates: {location.latitude}, {location.longitude}")
            print(f"   Timezone: {location.timezone}")
            if location.population:
                print(f"   Population: {location.population:,}")
    print()

    # Example 3: Get 3-day forecast for Tokyo
    print("3. 3-Day Forecast for Tokyo")
    print("-" * 80)
    tokyo_forecast = await get_weather_forecast(
        latitude=35.6762,
        longitude=139.6503,
        forecast_days=3,
        daily="temperature_2m_max,temperature_2m_min,precipitation_sum",
    )

    if tokyo_forecast.daily:
        daily = tokyo_forecast.daily
        for i in range(min(3, len(daily.time))):
            print(f"Date: {daily.time[i]}")
            temp_max = daily.temperature_2m_max[i] if daily.temperature_2m_max else None
            temp_min = daily.temperature_2m_min[i] if daily.temperature_2m_min else None
            precip = daily.precipitation_sum[i] if daily.precipitation_sum else None
            print(f"  High: {temp_max}°C | Low: {temp_min}°C | Precipitation: {precip}mm")
    print()

    # Example 4: Historical weather
    print("4. Historical Weather - Paris, January 1-7, 2024")
    print("-" * 80)
    historical = await get_historical_weather(
        latitude=48.8566,
        longitude=2.3522,
        start_date="2024-01-01",
        end_date="2024-01-07",
        daily="temperature_2m_max,temperature_2m_min",
    )

    if historical.daily:
        daily = historical.daily
        if daily.temperature_2m_max and daily.temperature_2m_min:
            avg_high = sum(daily.temperature_2m_max) / len(daily.temperature_2m_max)
            avg_low = sum(daily.temperature_2m_min) / len(daily.temperature_2m_min)

            print(f"Average High: {avg_high:.1f}°C")
            print(f"Average Low: {avg_low:.1f}°C")
            print(f"Coldest Day: {min(daily.temperature_2m_min)}°C")
            print(f"Warmest Day: {max(daily.temperature_2m_max)}°C")
    print()

    # Example 5: Air quality
    print("5. Air Quality - Los Angeles")
    print("-" * 80)
    air_quality = await get_air_quality(
        latitude=34.0522,
        longitude=-118.2437,
    )

    if air_quality.hourly:
        hourly = air_quality.hourly
        # Get first hour's data
        if hourly.time:
            print(f"Time: {hourly.time[0]}")
            if hourly.pm2_5 and hourly.pm2_5[0] is not None:
                print(f"PM2.5: {hourly.pm2_5[0]} µg/m³")
            if hourly.pm10 and hourly.pm10[0] is not None:
                print(f"PM10: {hourly.pm10[0]} µg/m³")
            if hourly.us_aqi and hourly.us_aqi[0] is not None:
                print(f"US AQI: {hourly.us_aqi[0]}")
    print()

    # Example 6: Marine forecast
    print("6. Marine Forecast - Hawaii")
    print("-" * 80)
    marine = await get_marine_forecast(
        latitude=21.3099,
        longitude=-157.8581,
    )

    if marine.hourly:
        hourly = marine.hourly
        # Get current conditions (first hour)
        if hourly.time:
            print(f"Time: {hourly.time[0]}")
            if hourly.wave_height and hourly.wave_height[0] is not None:
                print(f"Wave Height: {hourly.wave_height[0]}m")
            if hourly.wave_direction and hourly.wave_direction[0] is not None:
                print(f"Wave Direction: {hourly.wave_direction[0]}°")
            if hourly.wave_period and hourly.wave_period[0] is not None:
                print(f"Wave Period: {hourly.wave_period[0]}s")
    print()

    print("=" * 80)
    print("Examples completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
