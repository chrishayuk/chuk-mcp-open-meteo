#!/usr/bin/env python3
"""Trip planner example - demonstrates combining multiple weather tools.

This example shows how to use multiple tools together to plan a trip,
checking weather forecasts and air quality for your destination.
"""

import asyncio
from datetime import datetime
from chuk_mcp_open_meteo.server import (
    geocode_location,
    get_weather_forecast,
    get_air_quality,
)


async def plan_trip(destination: str, days: int = 7):
    """Plan a trip by checking weather and air quality.

    Args:
        destination: Location name (e.g., "Rome, Italy")
        days: Number of days to forecast
    """

    print(f"\n{'=' * 80}")
    print(f"TRIP PLANNER - {destination}")
    print(f"{'=' * 80}\n")

    # Step 1: Find the location
    print(f"📍 Finding {destination}...")
    locations = await geocode_location(name=destination, count=1)

    if not locations.get("results"):
        print(f"❌ Could not find {destination}")
        return

    location = locations["results"][0]
    lat = location["latitude"]
    lon = location["longitude"]

    print(f"✓ Found: {location['name']}, {location.get('country', 'Unknown')}")
    print(f"  Coordinates: {lat}, {lon}")
    print(f"  Timezone: {location.get('timezone', 'Unknown')}")
    if location.get("elevation"):
        print(f"  Elevation: {location['elevation']}m")
    print()

    # Step 2: Get weather forecast
    print(f"🌤️  Fetching {days}-day weather forecast...")
    weather = await get_weather_forecast(
        latitude=lat,
        longitude=lon,
        forecast_days=days,
        current_weather=True,
        daily="temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_hours,sunrise,sunset",
    )

    # Display current weather
    if "current_weather" in weather:
        current = weather["current_weather"]
        print("\n📊 Current Conditions:")
        print(f"  Temperature: {current.get('temperature')}°C")
        print(f"  Wind Speed: {current.get('windspeed')} km/h")

    # Display forecast
    if "daily" in weather:
        daily = weather["daily"]
        print(f"\n📅 {days}-Day Forecast:\n")

        dates = daily.get("time", [])
        temp_max = daily.get("temperature_2m_max", [])
        temp_min = daily.get("temperature_2m_min", [])
        precip_sum = daily.get("precipitation_sum", [])
        precip_hours = daily.get("precipitation_hours", [])
        sunrise = daily.get("sunrise", [])
        sunset = daily.get("sunset", [])

        for i in range(min(days, len(dates))):
            date = dates[i]
            # Parse date
            try:
                dt = datetime.fromisoformat(date)
                day_name = dt.strftime("%A")
            except (ValueError, TypeError):
                day_name = "Day"

            print(f"  {day_name}, {date}")
            print(f"    🌡️  High: {temp_max[i]}°C | Low: {temp_min[i]}°C")

            # Precipitation analysis
            if precip_sum[i] > 0:
                print(f"    🌧️  Precipitation: {precip_sum[i]}mm over {precip_hours[i]}h")
            else:
                print("    ☀️  No precipitation expected")

            # Sunrise/sunset if available
            if i < len(sunrise) and sunrise[i]:
                sr_time = sunrise[i].split("T")[1] if "T" in sunrise[i] else sunrise[i]
                ss_time = sunset[i].split("T")[1] if "T" in sunset[i] else sunset[i]
                print(f"    🌅 Sunrise: {sr_time} | 🌇 Sunset: {ss_time}")
            print()

        # Summary statistics
        avg_high = sum(temp_max) / len(temp_max)
        avg_low = sum(temp_min) / len(temp_min)
        total_precip = sum(precip_sum)
        rainy_days = sum(1 for p in precip_sum if p > 0.1)

        print("📈 Summary:")
        print(f"  Average High: {avg_high:.1f}°C")
        print(f"  Average Low: {avg_low:.1f}°C")
        print(f"  Total Precipitation: {total_precip:.1f}mm")
        print(f"  Rainy Days: {rainy_days}/{days}")

    print()

    # Step 3: Check air quality
    print("💨 Checking air quality...")
    air = await get_air_quality(latitude=lat, longitude=lon)

    if "hourly" in air:
        hourly = air["hourly"]

        # Get current or first available reading
        if hourly.get("time") and len(hourly["time"]) > 0:
            print("\n🏭 Air Quality (latest reading):")

            if "us_aqi" in hourly and hourly["us_aqi"] and hourly["us_aqi"][0]:
                aqi = hourly["us_aqi"][0]
                print(f"  US AQI: {aqi}")

                # Interpret AQI
                if aqi <= 50:
                    status = "Good 😊"
                    advice = "Air quality is satisfactory"
                elif aqi <= 100:
                    status = "Moderate 😐"
                    advice = "Acceptable for most people"
                elif aqi <= 150:
                    status = "Unhealthy for Sensitive Groups 😷"
                    advice = "Sensitive groups should limit outdoor activity"
                elif aqi <= 200:
                    status = "Unhealthy 😨"
                    advice = "Everyone should reduce prolonged outdoor exertion"
                else:
                    status = "Very Unhealthy/Hazardous ⚠️"
                    advice = "Avoid outdoor activities"

                print(f"  Status: {status}")
                print(f"  Advice: {advice}")

            if "pm2_5" in hourly and hourly["pm2_5"] and hourly["pm2_5"][0]:
                print(f"  PM2.5: {hourly['pm2_5'][0]} µg/m³")

            if "pm10" in hourly and hourly["pm10"] and hourly["pm10"][0]:
                print(f"  PM10: {hourly['pm10'][0]} µg/m³")

    print()

    # Step 4: Packing recommendations
    print("🎒 Packing Recommendations:")

    recommendations = []

    if avg_high > 25:
        recommendations.extend(["☀️ Sunscreen", "🕶️ Sunglasses", "🧢 Hat"])
    if avg_low < 10:
        recommendations.extend(["🧥 Warm jacket", "🧣 Scarf"])
    elif avg_low < 15:
        recommendations.append("🧥 Light jacket")

    if total_precip > 10:
        recommendations.extend(["☂️ Umbrella", "🥾 Waterproof shoes"])
    elif total_precip > 0:
        recommendations.append("☂️ Small umbrella (just in case)")

    if rainy_days > days / 2:
        recommendations.append("🧥 Rain jacket")

    for rec in recommendations:
        print(f"  {rec}")

    print(f"\n{'=' * 80}")
    print(f"Have a great trip to {destination}! ✈️")
    print(f"{'=' * 80}\n")


async def main():
    """Run trip planner examples."""

    # Example 1: Rome in spring
    await plan_trip("Rome, Italy", days=7)

    # Example 2: Tokyo
    await plan_trip("Tokyo, Japan", days=5)

    # Example 3: New York
    await plan_trip("New York, USA", days=7)


if __name__ == "__main__":
    asyncio.run(main())
