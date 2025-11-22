# Chuk MCP Open-Meteo

**The best weather MCP server ever** - A comprehensive Model Context Protocol (MCP) server for accessing Open-Meteo weather data.

[![PyPI version](https://badge.fury.io/py/chuk-mcp-open-meteo.svg)](https://badge.fury.io/py/chuk-mcp-open-meteo)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

This MCP server provides comprehensive access to Open-Meteo's weather APIs through five powerful tools:

### 1. Weather Forecast (`get_weather_forecast`)
Get detailed weather forecasts with customizable parameters:
- Current weather conditions
- Hourly forecasts (up to 16 days)
- Daily forecasts
- 50+ weather variables including temperature, precipitation, wind, humidity, cloud cover, and more
- Multiple units (celsius/fahrenheit, km/h, mph, m/s, knots)
- Automatic timezone detection

### 2. Location Geocoding (`geocode_location`)
Convert location names to coordinates:
- Search for any location worldwide
- Get coordinates, elevation, timezone
- Country and administrative information
- Population data where available
- Multi-language support

### 3. Historical Weather (`get_historical_weather`)
Access historical weather data:
- Data from 1940 onwards (location-dependent)
- Same comprehensive variables as forecasts
- Perfect for climate analysis and trends
- Hourly and daily aggregations

### 4. Air Quality (`get_air_quality`)
Monitor air quality and pollutants:
- PM2.5, PM10 particulate matter
- CO, NO2, SO2, O3 gas concentrations
- European AQI and US AQI indices
- Pollen data (multiple species)
- UV index
- Aerosol optical depth

### 5. Marine Forecast (`get_marine_forecast`)
Get marine weather conditions:
- Wave height, direction, and period
- Wind waves and swell waves separately
- Ocean current velocity and direction
- Up to 16-day forecasts
- Essential for maritime activities

## Installation

### From PyPI

```bash
pip install chuk-mcp-open-meteo
```

### From Source

```bash
git clone https://github.com/chrishayuk/chuk-mcp-open-meteo.git
cd chuk-mcp-open-meteo
pip install -e .
```

### Using uv (recommended for development)

```bash
git clone https://github.com/chrishayuk/chuk-mcp-open-meteo.git
cd chuk-mcp-open-meteo
uv sync --dev
```

## Usage

### With Claude Desktop

Add this configuration to your Claude Desktop config file:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "open-meteo": {
      "command": "chuk-mcp-open-meteo"
    }
  }
}
```

Or with uv:

```json
{
  "mcpServers": {
    "open-meteo": {
      "command": "uvx",
      "args": ["chuk-mcp-open-meteo"]
    }
  }
}
```

### Standalone

Run the server directly:

```bash
# STDIO mode (default, for MCP clients)
chuk-mcp-open-meteo

# HTTP mode (for web access)
chuk-mcp-open-meteo http
```

Or with Python:

```bash
# STDIO mode (default)
python -m chuk_mcp_open_meteo.server

# HTTP mode
python -m chuk_mcp_open_meteo.server http
```

**STDIO mode** is for MCP clients like Claude Desktop and mcp-cli.
**HTTP mode** runs a web server on http://localhost:8000 for HTTP-based MCP clients.

## Example Usage

Once configured, you can ask Claude questions like:

- "What's the current weather in London?"
- "Give me a 7-day forecast for Tokyo with hourly temperature and precipitation"
- "What was the weather like in New York on July 4th, 2020?"
- "What's the air quality in Los Angeles right now?"
- "What are the wave conditions off the coast of Hawaii?"
- "Find the coordinates for Paris, France"

### Python Examples

Check out the `examples/` directory for runnable Python examples:

```bash
# Basic usage of all tools
python examples/example_basic.py

# Advanced trip planning with multiple tools
python examples/example_trip_planner.py

# Test MCP protocol compliance
python examples/test_mcp_protocol.py

# Run all tests
./examples/test_all.sh
```

See [examples/README.md](examples/README.md) for detailed documentation.

## Tool Reference

### get_weather_forecast

```python
{
  "latitude": 51.5072,
  "longitude": -0.1276,
  "temperature_unit": "celsius",  # or "fahrenheit"
  "wind_speed_unit": "kmh",       # or "ms", "mph", "kn"
  "precipitation_unit": "mm",      # or "inch"
  "timezone": "auto",              # or specific timezone
  "forecast_days": 7,              # 1-16
  "current_weather": true,
  "hourly": "temperature_2m,precipitation,wind_speed_10m",
  "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum"
}
```

**Popular hourly variables**: `temperature_2m`, `relative_humidity_2m`, `precipitation`, `rain`, `snowfall`, `cloud_cover`, `wind_speed_10m`, `wind_direction_10m`, `pressure_msl`, `visibility`

**Popular daily variables**: `temperature_2m_max`, `temperature_2m_min`, `precipitation_sum`, `rain_sum`, `sunrise`, `sunset`, `wind_speed_10m_max`

### geocode_location

```python
{
  "name": "London",
  "count": 10,        # number of results
  "language": "en"    # language code
}
```

### get_historical_weather

```python
{
  "latitude": 40.7128,
  "longitude": -74.0060,
  "start_date": "2020-01-01",
  "end_date": "2020-01-31",
  "hourly": "temperature_2m,precipitation",
  "daily": "temperature_2m_max,temperature_2m_min"
}
```

### get_air_quality

```python
{
  "latitude": 34.0522,
  "longitude": -118.2437,
  "hourly": "pm10,pm2_5,us_aqi,european_aqi"
}
```

### get_marine_forecast

```python
{
  "latitude": 21.3099,
  "longitude": -157.8581,
  "hourly": "wave_height,wave_direction,wave_period"
}
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/chrishayuk/chuk-mcp-open-meteo.git
cd chuk-mcp-open-meteo

# Install with uv (recommended)
uv sync --dev

# Or with pip
pip install -e ".[dev]"
```

### Running Tests

```bash
make test              # Run tests
make test-cov          # Run tests with coverage
make coverage-report   # Show coverage report
```

### Code Quality

```bash
make lint      # Run linters
make format    # Auto-format code
make typecheck # Run type checking
make security  # Run security checks
make check     # Run all checks
```

### Building

```bash
make build         # Build package
make docker-build  # Build Docker image
```

## Deployment

### Fly.io

Deploy to Fly.io with a single command:

```bash
# First time setup
fly launch

# Deploy updates
fly deploy
```

The server will be available via HTTP at your Fly.io URL.

### Docker

```bash
# Build the image
docker build -t chuk-mcp-open-meteo .

# Run the container
docker run -p 8000:8000 chuk-mcp-open-meteo
```

## API Credits

This server uses the free [Open-Meteo API](https://open-meteo.com/). Open-Meteo provides:

- Free access for non-commercial use
- No API key required
- High-resolution weather models
- 25+ global weather models
- Historical data from 1940
- No rate limits for reasonable use

Please consider [supporting Open-Meteo](https://open-meteo.com/en/pricing) if you use this extensively.

## Architecture

Built on top of [chuk-mcp-server](https://github.com/chrishayuk/chuk-mcp-server), this server uses:

- **Fast & Simple**: Decorator-based tool definitions
- **Type-Safe**: Automatic JSON-RPC schema generation from Python type hints
- **Async**: Native async/await support for optimal performance
- **Production-Ready**: Sub-3ms latency, 36,000+ RPS capability

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Open-Meteo](https://open-meteo.com/) for providing excellent free weather data
- [Model Context Protocol](https://modelcontextprotocol.io/) for the MCP specification
- [Anthropic](https://www.anthropic.com/) for Claude and MCP support

## Support

- GitHub Issues: [Report bugs or request features](https://github.com/chrishayuk/chuk-mcp-open-meteo/issues)
- Documentation: [Open-Meteo API Docs](https://open-meteo.com/en/docs)

---

**Made with ❤️ by [Chris Hay](https://github.com/chrishayuk)**
