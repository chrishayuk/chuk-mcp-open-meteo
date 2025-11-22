#!/usr/bin/env python3
"""Interactive demo of the Open-Meteo MCP Server.

This script provides an interactive CLI to test all the weather tools.
"""

import asyncio
import sys
from chuk_mcp_open_meteo.server import (
    get_weather_forecast,
    geocode_location,
    get_historical_weather,
    get_air_quality,
    get_marine_forecast,
)


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_menu():
    """Print the main menu."""
    print_header("Open-Meteo MCP Server - Interactive Demo")
    print("Choose a weather tool to test:\n")
    print("  1. 🌤️  Get Weather Forecast")
    print("  2. 📍 Geocode Location")
    print("  3. 📅 Get Historical Weather")
    print("  4. 💨 Get Air Quality")
    print("  5. 🌊 Get Marine Forecast")
    print("  6. 🎯 Quick Demo (all tools)")
    print("  0. ❌ Exit")
    print()


async def demo_weather_forecast():
    """Demo the weather forecast tool."""
    print_header("Weather Forecast Demo")

    print("Let's get the weather forecast for a location.\n")

    # Get location
    city = input("Enter city name (or press Enter for 'London'): ").strip() or "London"

    # Geocode
    print(f"\n🔍 Finding {city}...")
    locations = await geocode_location(name=city, count=1)

    if not locations.get("results"):
        print(f"❌ Could not find {city}")
        return

    location = locations["results"][0]
    lat = location["latitude"]
    lon = location["longitude"]

    print(f"✓ Found: {location['name']}, {location.get('country', 'Unknown')}")
    print(f"  Coordinates: {lat}, {lon}\n")

    # Get forecast
    days = input("How many days to forecast? (1-16, default 7): ").strip()
    try:
        days = int(days) if days else 7
        days = max(1, min(16, days))
    except (ValueError, TypeError):
        days = 7

    print(f"\n📊 Fetching {days}-day forecast...\n")

    weather = await get_weather_forecast(
        latitude=lat,
        longitude=lon,
        forecast_days=days,
        current_weather=True,
        daily="temperature_2m_max,temperature_2m_min,precipitation_sum",
    )

    # Display current weather
    if "current_weather" in weather:
        current = weather["current_weather"]
        print("Current Conditions:")
        print(f"  🌡️  Temperature: {current.get('temperature')}°C")
        print(f"  💨 Wind Speed: {current.get('windspeed')} km/h")
        print(f"  🧭 Wind Direction: {current.get('winddirection')}°")
        print()

    # Display forecast
    if "daily" in weather:
        daily = weather["daily"]
        print(f"{days}-Day Forecast:\n")

        dates = daily.get("time", [])
        temp_max = daily.get("temperature_2m_max", [])
        temp_min = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])

        for i in range(min(days, len(dates))):
            precip_str = f"{precip[i]}mm" if precip[i] > 0 else "No rain"
            print(f"  {dates[i]}: {temp_min[i]}°C - {temp_max[i]}°C, {precip_str}")

    input("\nPress Enter to continue...")


async def demo_geocode():
    """Demo the geocoding tool."""
    print_header("Location Geocoding Demo")

    location_name = input("Enter location to search for: ").strip()
    if not location_name:
        print("❌ No location entered")
        return

    count = input("How many results? (default 5): ").strip()
    try:
        count = int(count) if count else 5
    except (ValueError, TypeError):
        count = 5

    print(f"\n🔍 Searching for '{location_name}'...\n")

    results = await geocode_location(name=location_name, count=count)

    if not results.get("results"):
        print(f"❌ No results found for '{location_name}'")
        return

    print(f"Found {len(results['results'])} location(s):\n")

    for i, loc in enumerate(results["results"], 1):
        print(f"{i}. {loc.get('name')}, {loc.get('country', 'Unknown')}")
        print(f"   📍 {loc.get('latitude')}, {loc.get('longitude')}")
        print(f"   🕐 Timezone: {loc.get('timezone', 'Unknown')}")
        if loc.get("population"):
            print(f"   👥 Population: {loc['population']:,}")
        print()

    input("Press Enter to continue...")


async def demo_historical():
    """Demo the historical weather tool."""
    print_header("Historical Weather Demo")

    city = input("Enter city name: ").strip()
    if not city:
        print("❌ No city entered")
        return

    # Geocode
    print(f"\n🔍 Finding {city}...")
    locations = await geocode_location(name=city, count=1)

    if not locations.get("results"):
        print(f"❌ Could not find {city}")
        return

    location = locations["results"][0]
    lat = location["latitude"]
    lon = location["longitude"]
    print(f"✓ Found: {location['name']}, {location.get('country', 'Unknown')}\n")

    start_date = input("Start date (YYYY-MM-DD, e.g., 2024-01-01): ").strip()
    end_date = input("End date (YYYY-MM-DD, e.g., 2024-01-07): ").strip()

    if not start_date or not end_date:
        print("❌ Invalid dates")
        return

    print(f"\n📅 Fetching historical data for {start_date} to {end_date}...\n")

    historical = await get_historical_weather(
        latitude=lat,
        longitude=lon,
        start_date=start_date,
        end_date=end_date,
        daily="temperature_2m_max,temperature_2m_min,precipitation_sum",
    )

    if "daily" in historical:
        daily = historical["daily"]
        dates = daily.get("time", [])
        temp_max = daily.get("temperature_2m_max", [])
        temp_min = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])

        for i in range(len(dates)):
            print(f"{dates[i]}: {temp_min[i]}°C - {temp_max[i]}°C, {precip[i]}mm rain")

        print("\n📊 Summary:")
        print(f"  Average High: {sum(temp_max) / len(temp_max):.1f}°C")
        print(f"  Average Low: {sum(temp_min) / len(temp_min):.1f}°C")
        print(f"  Total Precipitation: {sum(precip):.1f}mm")

    input("\nPress Enter to continue...")


async def demo_air_quality():
    """Demo the air quality tool."""
    print_header("Air Quality Demo")

    city = input("Enter city name: ").strip() or "Los Angeles"

    # Geocode
    print(f"\n🔍 Finding {city}...")
    locations = await geocode_location(name=city, count=1)

    if not locations.get("results"):
        print(f"❌ Could not find {city}")
        return

    location = locations["results"][0]
    lat = location["latitude"]
    lon = location["longitude"]
    print(f"✓ Found: {location['name']}, {location.get('country', 'Unknown')}\n")

    print("💨 Fetching air quality data...\n")

    air = await get_air_quality(latitude=lat, longitude=lon)

    if "hourly" in air:
        hourly = air["hourly"]

        if hourly.get("time"):
            print("Air Quality (latest reading):\n")

            if "us_aqi" in hourly and hourly["us_aqi"] and hourly["us_aqi"][0]:
                aqi = hourly["us_aqi"][0]
                print(f"  📊 US AQI: {aqi}")

                if aqi <= 50:
                    status = "Good 😊"
                elif aqi <= 100:
                    status = "Moderate 😐"
                elif aqi <= 150:
                    status = "Unhealthy for Sensitive Groups 😷"
                else:
                    status = "Unhealthy 😨"

                print(f"  Status: {status}")

            if "pm2_5" in hourly and hourly["pm2_5"] and hourly["pm2_5"][0]:
                print(f"  🌫️  PM2.5: {hourly['pm2_5'][0]} µg/m³")

            if "pm10" in hourly and hourly["pm10"] and hourly["pm10"][0]:
                print(f"  🌫️  PM10: {hourly['pm10'][0]} µg/m³")

    input("\nPress Enter to continue...")


async def demo_marine():
    """Demo the marine forecast tool."""
    print_header("Marine Forecast Demo")

    print("Enter coordinates for ocean location")
    print("(e.g., Hawaii: 21.3099, -157.8581)\n")

    lat_str = input("Latitude: ").strip()
    lon_str = input("Longitude: ").strip()

    try:
        lat = float(lat_str)
        lon = float(lon_str)
    except (ValueError, TypeError):
        print("❌ Invalid coordinates")
        return

    print("\n🌊 Fetching marine forecast...\n")

    marine = await get_marine_forecast(latitude=lat, longitude=lon)

    if "hourly" in marine:
        hourly = marine["hourly"]

        if hourly.get("time"):
            print("Marine Conditions (current):\n")

            if "wave_height" in hourly and hourly["wave_height"]:
                print(f"  🌊 Wave Height: {hourly['wave_height'][0]}m")

            if "wave_direction" in hourly and hourly["wave_direction"]:
                print(f"  🧭 Wave Direction: {hourly['wave_direction'][0]}°")

            if "wave_period" in hourly and hourly["wave_period"]:
                print(f"  ⏱️  Wave Period: {hourly['wave_period'][0]}s")

            if "wind_wave_height" in hourly and hourly["wind_wave_height"]:
                print(f"  💨 Wind Wave Height: {hourly['wind_wave_height'][0]}m")

            if "swell_wave_height" in hourly and hourly["swell_wave_height"]:
                print(f"  🌊 Swell Wave Height: {hourly['swell_wave_height'][0]}m")

    input("\nPress Enter to continue...")


async def quick_demo():
    """Run a quick demo of all tools."""
    print_header("Quick Demo - All Tools")

    print("Running quick demo with London...\n")

    # Weather
    print("1. ☀️  Weather Forecast")
    weather = await get_weather_forecast(
        latitude=51.5072,
        longitude=-0.1276,
        current_weather=True,
    )
    if "current_weather" in weather:
        print(f"   Temperature: {weather['current_weather']['temperature']}°C")

    # Geocode
    print("\n2. 📍 Geocoding")
    locations = await geocode_location(name="Paris", count=2)
    if locations.get("results"):
        print(f"   Found: {locations['results'][0]['name']}, {locations['results'][0]['country']}")

    # Historical
    print("\n3. 📅 Historical Weather")
    historical = await get_historical_weather(
        latitude=51.5072,
        longitude=-0.1276,
        start_date="2024-01-01",
        end_date="2024-01-07",
        daily="temperature_2m_max",
    )
    if "daily" in historical:
        avg = sum(historical["daily"]["temperature_2m_max"]) / len(
            historical["daily"]["temperature_2m_max"]
        )
        print(f"   Jan 2024 avg high: {avg:.1f}°C")

    # Air quality
    print("\n4. 💨 Air Quality")
    air = await get_air_quality(latitude=51.5072, longitude=-0.1276)
    if "hourly" in air and "us_aqi" in air["hourly"]:
        print(f"   US AQI: {air['hourly']['us_aqi'][0] if air['hourly']['us_aqi'][0] else 'N/A'}")

    # Marine
    print("\n5. 🌊 Marine Forecast")
    marine = await get_marine_forecast(latitude=21.3099, longitude=-157.8581)
    if "hourly" in marine and "wave_height" in marine["hourly"]:
        print(f"   Wave height: {marine['hourly']['wave_height'][0]}m")

    print("\n✓ All tools working!\n")
    input("Press Enter to continue...")


async def main():
    """Main interactive loop."""

    while True:
        print_menu()

        choice = input("Enter your choice (0-6): ").strip()

        try:
            if choice == "0":
                print("\n👋 Goodbye!\n")
                break
            elif choice == "1":
                await demo_weather_forecast()
            elif choice == "2":
                await demo_geocode()
            elif choice == "3":
                await demo_historical()
            elif choice == "4":
                await demo_air_quality()
            elif choice == "5":
                await demo_marine()
            elif choice == "6":
                await quick_demo()
            else:
                print("\n❌ Invalid choice. Please enter 0-6.\n")
                input("Press Enter to continue...")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
            input("Press Enter to continue...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!\n")
        sys.exit(0)
