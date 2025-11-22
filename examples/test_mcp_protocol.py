#!/usr/bin/env python3
"""Test the MCP server protocol implementation.

This script tests the MCP server by sending JSON-RPC requests
and validating the responses according to the MCP specification.
"""

import asyncio
import json
import sys
from typing import Any


class MCPClient:
    """Simple MCP client for testing the server."""

    def __init__(self):
        self.request_id = 0
        self.process = None

    async def start_server(self):
        """Start the MCP server as a subprocess."""
        print("Starting MCP server...")
        self.process = await asyncio.create_subprocess_exec(
            sys.executable,
            "-m",
            "chuk_mcp_open_meteo.server",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        print("✓ Server started")

    async def stop_server(self):
        """Stop the MCP server."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            print("✓ Server stopped")

    async def send_request(self, method: str, params: dict[str, Any] = None) -> dict:
        """Send a JSON-RPC request to the server.

        Args:
            method: The method to call
            params: Parameters for the method

        Returns:
            The response from the server
        """
        self.request_id += 1

        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
        }

        if params is not None:
            request["params"] = params

        # Send request
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()

        # Read response
        response_line = await self.process.stdout.readline()
        response = json.loads(response_line.decode())

        return response

    async def initialize(self) -> dict:
        """Initialize the MCP session."""
        return await self.send_request(
            "initialize",
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"},
            },
        )


async def test_initialize():
    """Test MCP server initialization."""
    print("\n" + "=" * 80)
    print("TEST: Server Initialization")
    print("=" * 80)

    client = MCPClient()
    await client.start_server()

    try:
        response = await client.initialize()

        print("Request: initialize")
        print(f"Response: {json.dumps(response, indent=2)}")

        # Validate response
        assert "result" in response, "Response should have 'result'"
        result = response["result"]

        assert "protocolVersion" in result, "Should return protocol version"
        assert "serverInfo" in result, "Should return server info"
        assert "capabilities" in result, "Should return capabilities"

        print("\n✓ Initialization test passed")

    finally:
        await client.stop_server()


async def test_list_tools():
    """Test listing available tools."""
    print("\n" + "=" * 80)
    print("TEST: List Tools")
    print("=" * 80)

    client = MCPClient()
    await client.start_server()

    try:
        # Initialize first
        await client.initialize()

        # List tools
        response = await client.send_request("tools/list")

        print("Request: tools/list")
        print(f"Response: {json.dumps(response, indent=2)}")

        # Validate response
        assert "result" in response, "Response should have 'result'"
        result = response["result"]

        assert "tools" in result, "Should return tools list"
        tools = result["tools"]

        assert len(tools) >= 5, "Should have at least 5 tools"

        # Check for expected tools
        tool_names = [tool["name"] for tool in tools]
        expected_tools = [
            "get_weather_forecast",
            "geocode_location",
            "get_historical_weather",
            "get_air_quality",
            "get_marine_forecast",
        ]

        for expected in expected_tools:
            assert expected in tool_names, f"Should have {expected} tool"

        print(f"\n✓ Found {len(tools)} tools")
        for tool in tools:
            print(f"  - {tool['name']}: {tool.get('description', 'No description')[:60]}...")

        print("\n✓ List tools test passed")

    finally:
        await client.stop_server()


async def test_call_weather_forecast():
    """Test calling the weather forecast tool."""
    print("\n" + "=" * 80)
    print("TEST: Call Weather Forecast Tool")
    print("=" * 80)

    client = MCPClient()
    await client.start_server()

    try:
        # Initialize
        await client.initialize()

        # Call weather forecast for London
        response = await client.send_request(
            "tools/call",
            {
                "name": "get_weather_forecast",
                "arguments": {"latitude": 51.5072, "longitude": -0.1276, "current_weather": True},
            },
        )

        print("Request: tools/call - get_weather_forecast")
        print("Arguments: London (51.5072, -0.1276)")

        # Validate response
        assert "result" in response, "Response should have 'result'"
        result = response["result"]

        # The result should contain the weather data
        assert "content" in result or "latitude" in result, "Should return weather data"

        print(f"Response preview: {json.dumps(result, indent=2)[:500]}...")
        print("\n✓ Weather forecast tool test passed")

    finally:
        await client.stop_server()


async def test_call_geocode():
    """Test calling the geocode tool."""
    print("\n" + "=" * 80)
    print("TEST: Call Geocode Location Tool")
    print("=" * 80)

    client = MCPClient()
    await client.start_server()

    try:
        # Initialize
        await client.initialize()

        # Call geocode
        response = await client.send_request(
            "tools/call", {"name": "geocode_location", "arguments": {"name": "Paris", "count": 3}}
        )

        print("Request: tools/call - geocode_location")
        print("Arguments: name='Paris', count=3")

        # Validate response
        assert "result" in response, "Response should have 'result'"
        result = response["result"]

        print(f"Response preview: {json.dumps(result, indent=2)[:500]}...")
        print("\n✓ Geocode tool test passed")

    finally:
        await client.stop_server()


async def test_error_handling():
    """Test error handling with invalid requests."""
    print("\n" + "=" * 80)
    print("TEST: Error Handling")
    print("=" * 80)

    client = MCPClient()
    await client.start_server()

    try:
        # Initialize
        await client.initialize()

        # Test 1: Call non-existent tool
        print("\nTest 1: Non-existent tool")
        response = await client.send_request(
            "tools/call", {"name": "non_existent_tool", "arguments": {}}
        )

        assert "error" in response, "Should return error for non-existent tool"
        print(f"✓ Correctly returned error: {response['error'].get('message')}")

        # Test 2: Call with invalid arguments
        print("\nTest 2: Invalid arguments")
        response = await client.send_request(
            "tools/call",
            {
                "name": "get_weather_forecast",
                "arguments": {
                    # Missing required latitude/longitude
                    "current_weather": True
                },
            },
        )

        # Should either error or handle gracefully
        if "error" in response:
            print(f"✓ Correctly returned error: {response['error'].get('message')}")
        else:
            print("✓ Handled invalid arguments gracefully")

        print("\n✓ Error handling test passed")

    finally:
        await client.stop_server()


async def main():
    """Run all MCP protocol tests."""

    print("\n" + "=" * 80)
    print("MCP PROTOCOL TESTS - chuk-mcp-open-meteo")
    print("=" * 80)

    tests = [
        ("Initialize", test_initialize),
        ("List Tools", test_list_tools),
        ("Weather Forecast", test_call_weather_forecast),
        ("Geocode Location", test_call_geocode),
        ("Error Handling", test_error_handling),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            print(f"\n❌ Test '{name}' failed: {e}")
            import traceback

            traceback.print_exc()
            failed += 1

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    if failed == 0:
        print("\n✓ All tests passed! 🎉")
        return 0
    else:
        print(f"\n❌ {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
