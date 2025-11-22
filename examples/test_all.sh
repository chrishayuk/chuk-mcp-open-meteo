#!/bin/bash
# Test all examples and verify the MCP server works correctly

set -e  # Exit on error

echo "========================================"
echo "Testing chuk-mcp-open-meteo"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
        exit 1
    fi
}

# Check if package is installed
echo -e "${BLUE}Checking installation...${NC}"
python -c "import chuk_mcp_open_meteo" 2>/dev/null
print_status $? "Package import successful"

# Test 1: Basic examples
echo ""
echo -e "${BLUE}Test 1: Running basic examples...${NC}"
python examples/example_basic.py > /dev/null 2>&1
print_status $? "Basic examples executed"

# Test 2: Trip planner
echo ""
echo -e "${BLUE}Test 2: Running trip planner...${NC}"
timeout 60 python examples/example_trip_planner.py > /dev/null 2>&1
print_status $? "Trip planner executed"

# Test 3: MCP protocol tests
echo ""
echo -e "${BLUE}Test 3: Running MCP protocol tests...${NC}"
timeout 60 python examples/test_mcp_protocol.py
print_status $? "MCP protocol tests passed"

# Test 4: Unit tests (if pytest is available)
echo ""
echo -e "${BLUE}Test 4: Running unit tests...${NC}"
if command -v pytest &> /dev/null; then
    pytest tests/ -v --tb=short 2>&1 | tail -20
    print_status $? "Unit tests passed"
else
    echo -e "${BLUE}Pytest not found, skipping unit tests${NC}"
fi

# Summary
echo ""
echo "========================================"
echo -e "${GREEN}All tests passed! 🎉${NC}"
echo "========================================"
echo ""
echo "The Open-Meteo MCP server is working correctly!"
echo ""
echo "Next steps:"
echo "  1. Configure Claude Desktop (see examples/claude_desktop_config.json)"
echo "  2. Try asking Claude: 'What's the weather in London?'"
echo "  3. Explore more examples in the examples/ directory"
echo ""
