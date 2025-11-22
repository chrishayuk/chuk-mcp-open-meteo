# Usage Examples

This document provides practical examples of using the Open-Meteo MCP Server with Claude.

## Table of Contents

- [Basic Weather Queries](#basic-weather-queries)
- [Advanced Forecast Requests](#advanced-forecast-requests)
- [Historical Weather Analysis](#historical-weather-analysis)
- [Air Quality Monitoring](#air-quality-monitoring)
- [Marine Weather](#marine-weather)
- [Location Geocoding](#location-geocoding)
- [Complex Multi-Tool Workflows](#complex-multi-tool-workflows)

## Basic Weather Queries

### Current Weather

```
You: What's the weather like in London right now?

Claude: I'll get the current weather for London.
[Uses geocode_location to find London coordinates]
[Uses get_weather_forecast with current_weather=true]

Response: Currently in London, UK:
- Temperature: 15°C (59°F)
- Conditions: Partly cloudy
- Wind: 12 km/h from the west
- Humidity: 72%
- Pressure: 1013 hPa
```

### Simple Forecast

```
You: Give me a 3-day forecast for Tokyo

Claude: [Uses geocode_location for Tokyo]
[Uses get_weather_forecast with forecast_days=3, daily variables]

Response: 3-Day Forecast for Tokyo, Japan:

Day 1 (Tomorrow):
- High: 22°C / Low: 16°C
- Precipitation: 2mm (light rain expected)
- Sunrise: 5:42 AM / Sunset: 6:28 PM

Day 2:
- High: 24°C / Low: 18°C
- Precipitation: 0mm (clear)
...
```

## Advanced Forecast Requests

### Detailed Hourly Forecast

```
You: I need a detailed hourly forecast for the next 24 hours in San Francisco.
     Include temperature, feels-like temperature, precipitation, wind speed,
     and cloud cover.

Claude: [Uses get_weather_forecast with specific hourly variables]

hourly variables: "temperature_2m,apparent_temperature,precipitation,
                   wind_speed_10m,cloud_cover"
```

### Custom Units

```
You: What's the weather in Miami? Use Fahrenheit and mph for wind.

Claude: [Uses get_weather_forecast with:]
temperature_unit: "fahrenheit"
wind_speed_unit: "mph"
```

### Extended Forecast

```
You: Give me a 2-week forecast for Oslo with daily temperature extremes
     and total precipitation.

Claude: [Uses get_weather_forecast with:]
forecast_days: 14
daily: "temperature_2m_max,temperature_2m_min,precipitation_sum"
```

## Historical Weather Analysis

### Specific Date Range

```
You: What was the weather like in Paris during the first week of July 2023?

Claude: [Uses geocode_location for Paris]
[Uses get_historical_weather with:]
start_date: "2023-07-01"
end_date: "2023-07-07"
daily: "temperature_2m_max,temperature_2m_min,precipitation_sum"

Response: Paris weather July 1-7, 2023:
- Average high: 28°C
- Average low: 18°C
- Total precipitation: 12mm
- Hottest day: July 4 (31°C)
```

### Climate Comparison

```
You: Compare the average temperatures in New York for January 2024 vs January 2023

Claude: [Makes two get_historical_weather calls]
First: start_date: "2023-01-01", end_date: "2023-01-31"
Second: start_date: "2024-01-01", end_date: "2024-01-31"
[Calculates and compares averages]
```

### Precipitation Analysis

```
You: How much rain fell in Seattle in March 2024? Break it down by week.

Claude: [Uses get_historical_weather with:]
hourly: "precipitation"
[Groups and sums by week]
```

## Air Quality Monitoring

### Current Air Quality

```
You: What's the air quality in Los Angeles right now?

Claude: [Uses get_air_quality with default parameters]

Response: Los Angeles Air Quality:
- US AQI: 87 (Moderate)
- PM2.5: 28 µg/m³
- PM10: 45 µg/m³
- Ozone (O3): 65 µg/m³
- NO2: 32 µg/m³

Health recommendation: Air quality is acceptable for most people.
Sensitive groups should consider reducing prolonged outdoor exposure.
```

### Pollen Forecast

```
You: I have allergies. What's the pollen situation in Amsterdam this week?

Claude: [Uses get_air_quality with:]
hourly: "grass_pollen,birch_pollen,alder_pollen,ragweed_pollen"
[Returns hourly pollen concentrations]
```

### Multi-Pollutant Analysis

```
You: Show me the pollution levels in Beijing, including all major pollutants

Claude: [Uses get_air_quality with:]
hourly: "pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,
         sulphur_dioxide,ozone,us_aqi,european_aqi"
```

## Marine Weather

### Surf Conditions

```
You: What are the surf conditions in Bali right now?

Claude: [Uses geocode_location for Bali coastal area]
[Uses get_marine_forecast]

Response: Marine conditions off Bali:
- Wave height: 1.8m
- Wave period: 12 seconds
- Wave direction: Southwest (225°)
- Swell wave height: 1.5m
- Wind wave height: 0.3m

Good surfing conditions with moderate swell!
```

### Sailing Weather

```
You: I'm planning to sail from San Diego this weekend.
     What are the marine conditions for Saturday and Sunday?

Claude: [Uses get_marine_forecast with:]
forecast_days: 3
hourly: "wave_height,wave_direction,wind_wave_height,ocean_current_velocity"
[Filters for Saturday/Sunday]
```

### Fishing Conditions

```
You: What are the ocean conditions for fishing off the coast of Maine tomorrow?

Claude: [Uses get_marine_forecast]
[Also uses get_weather_forecast for weather conditions]
[Combines marine and weather data]
```

## Location Geocoding

### Find Coordinates

```
You: What are the coordinates for Barcelona?

Claude: [Uses geocode_location with name="Barcelona"]

Response: Barcelona, Spain:
- Latitude: 41.3874
- Longitude: 2.1686
- Elevation: 12m
- Timezone: Europe/Madrid
- Population: 1,620,343
```

### Disambiguate Locations

```
You: Find Paris

Claude: [Uses geocode_location with count=10]

Response: Found multiple locations named "Paris":
1. Paris, France (48.8566, 2.3522) - Pop: 2,165,423
2. Paris, Texas, USA (33.6609, -95.5555) - Pop: 24,699
3. Paris, Tennessee, USA (36.3020, -88.3267) - Pop: 10,156
...

Which Paris did you mean?
```

### Search in Different Languages

```
You: Find Munich in German

Claude: [Uses geocode_location with:]
name: "München"
language: "de"
```

## Complex Multi-Tool Workflows

### Trip Planning

```
You: I'm planning a trip to Rome next week. What should I pack based on the weather?
     Also, is air quality okay?

Claude:
[Uses geocode_location for Rome]
[Uses get_weather_forecast for next 7 days with temperature, precipitation]
[Uses get_air_quality for air quality data]

Response: Rome next week (March 15-21):

Weather:
- Temperature range: 12-18°C (54-64°F)
- Light rain expected on March 17-18 (15mm total)
- Mostly sunny other days

Packing recommendations:
✓ Light jacket or sweater
✓ Umbrella for midweek
✓ Layers for variable temperatures
✓ Sunglasses for sunny days

Air Quality:
- European AQI: 35 (Good)
- No concerns for outdoor activities

Perfect time to visit!
```

### Event Weather Planning

```
You: I'm organizing an outdoor wedding in Napa Valley on June 15, 2024.
     What was the weather like on that date historically? And what's the
     forecast if the date is coming up?

Claude:
[Checks if date is past or future]
[Uses get_historical_weather for past June 15ths to show typical conditions]
[Uses get_weather_forecast if date is within forecast range]
[Provides probability analysis and recommendations]
```

### Climate Research

```
You: I'm writing a paper on temperature trends. Compare average temperatures
     in Phoenix, AZ for summer months (June-August) over the last 3 years.

Claude:
[Uses geocode_location for Phoenix]
[Makes multiple get_historical_weather calls for:]
  - June-August 2022
  - June-August 2023
  - June-August 2024
[Calculates statistics: mean, max, min, trends]
[Creates comparison analysis]
```

### Marine Activity Planning

```
You: I want to go scuba diving in the Great Barrier Reef next Tuesday.
     What are the weather and marine conditions?

Claude:
[Uses geocode_location for Great Barrier Reef location]
[Uses get_weather_forecast for general weather]
[Uses get_marine_forecast for wave height, currents, visibility factors]
[Assesses diving conditions and provides recommendations]
```

## Tips for Best Results

1. **Be Specific**: Include location names, date ranges, and specific weather parameters
2. **Use Natural Language**: Claude understands conversational requests
3. **Combine Questions**: Ask for multiple aspects in one query (weather + air quality, etc.)
4. **Specify Units**: Mention if you want Fahrenheit, mph, etc.
5. **Request Formatting**: Ask for tables, charts, or specific output formats
6. **Historical Context**: For past events, provide exact dates for accurate historical data

## Weather Variables Quick Reference

### Most Common Hourly Variables
- `temperature_2m` - Temperature at 2 meters
- `precipitation` - Total precipitation
- `wind_speed_10m` - Wind speed at 10 meters
- `cloud_cover` - Cloud cover percentage
- `relative_humidity_2m` - Relative humidity

### Most Common Daily Variables
- `temperature_2m_max` - Maximum daily temperature
- `temperature_2m_min` - Minimum daily temperature
- `precipitation_sum` - Total daily precipitation
- `sunrise` - Sunrise time
- `sunset` - Sunset time

### Air Quality Variables
- `pm2_5` - Fine particulate matter
- `pm10` - Coarse particulate matter
- `us_aqi` - US Air Quality Index
- `european_aqi` - European Air Quality Index

### Marine Variables
- `wave_height` - Significant wave height
- `wave_direction` - Wave direction
- `wave_period` - Wave period
- `ocean_current_velocity` - Ocean current speed
