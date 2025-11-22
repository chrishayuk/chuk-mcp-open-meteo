#!/bin/bash
# Quick test script for the Open-Meteo MCP server using mcp-cli
# This script tests all 5 tools and verifies they work correctly

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Open-Meteo MCP Server Test${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if mcp-cli is installed
if ! command -v mcp-cli &> /dev/null; then
    echo -e "${RED}Error: mcp-cli not found${NC}"
    echo "Install with: pip install mcp-cli"
    exit 1
fi

# Check if server is installed
if ! python -c "import chuk_mcp_open_meteo" 2>/dev/null; then
    echo -e "${RED}Error: chuk-mcp-open-meteo not installed${NC}"
    echo "Install with: pip install chuk-mcp-open-meteo"
    exit 1
fi

echo -e "${GREEN}✓ Prerequisites installed${NC}"
echo ""

# Test 1: List tools
echo -e "${YELLOW}Test 1: Listing available tools...${NC}"
mcp-cli --server "python -m chuk_mcp_open_meteo.server" tools 2>/dev/null | head -20
echo -e "${GREEN}✓ Tools listed${NC}"
echo ""

# Test 2: Weather forecast
echo -e "${YELLOW}Test 2: Testing weather forecast (London)...${NC}"
result=$(mcp-cli --server "python -m chuk_mcp_open_meteo.server" cmd call-tool \
  --name get_weather_forecast \
  --params '{"latitude": 51.5072, "longitude": -0.1276, "current_weather": true}' 2>/dev/null)

if echo "$result" | grep -q "temperature"; then
    echo -e "${GREEN}✓ Weather forecast working${NC}"
    echo "$result" | head -15
else
    echo -e "${RED}✗ Weather forecast failed${NC}"
    exit 1
fi
echo ""

# Test 3: Geocoding
echo -e "${YELLOW}Test 3: Testing geocoding (Paris)...${NC}"
result=$(mcp-cli --server "python -m chuk_mcp_open_meteo.server" cmd call-tool \
  --name geocode_location \
  --params '{"name": "Paris", "count": 2}' 2>/dev/null)

if echo "$result" | grep -q "France"; then
    echo -e "${GREEN}✓ Geocoding working${NC}"
    echo "$result" | head -15
else
    echo -e "${RED}✗ Geocoding failed${NC}"
    exit 1
fi
echo ""

# Test 4: Historical weather
echo -e "${YELLOW}Test 4: Testing historical weather (Paris, Jan 2024)...${NC}"
result=$(mcp-cli --server "python -m chuk_mcp_open_meteo.server" cmd call-tool \
  --name get_historical_weather \
  --params '{"latitude": 48.8566, "longitude": 2.3522, "start_date": "2024-01-01", "end_date": "2024-01-07", "daily": "temperature_2m_max"}' 2>/dev/null)

if echo "$result" | grep -q "temperature"; then
    echo -e "${GREEN}✓ Historical weather working${NC}"
    echo "$result" | head -15
else
    echo -e "${RED}✗ Historical weather failed${NC}"
    exit 1
fi
echo ""

# Test 5: Air quality
echo -e "${YELLOW}Test 5: Testing air quality (Los Angeles)...${NC}"
result=$(mcp-cli --server "python -m chuk_mcp_open_meteo.server" cmd call-tool \
  --name get_air_quality \
  --params '{"latitude": 34.0522, "longitude": -118.2437}' 2>/dev/null)

if echo "$result" | grep -q "pm"; then
    echo -e "${GREEN}✓ Air quality working${NC}"
    echo "$result" | head -15
else
    echo -e "${RED}✗ Air quality failed${NC}"
    exit 1
fi
echo ""

# Test 6: Marine forecast
echo -e "${YELLOW}Test 6: Testing marine forecast (Hawaii)...${NC}"
result=$(mcp-cli --server "python -m chuk_mcp_open_meteo.server" cmd call-tool \
  --name get_marine_forecast \
  --params '{"latitude": 21.3099, "longitude": -157.8581}' 2>/dev/null)

if echo "$result" | grep -q "wave"; then
    echo -e "${GREEN}✓ Marine forecast working${NC}"
    echo "$result" | head -15
else
    echo -e "${RED}✗ Marine forecast failed${NC}"
    exit 1
fi
echo ""

# Summary
echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}All tests passed! 🎉${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo "The Open-Meteo MCP server is working correctly with mcp-cli."
echo ""
echo "Next steps:"
echo "  1. Add to your mcp config: cp examples/mcp_config.json ~/.mcp/config.json"
echo "  2. Start interactive session: mcp-cli --server weather --provider openai --model gpt-4o"
echo "  3. Try: 'What's the weather in London?'"
echo ""
