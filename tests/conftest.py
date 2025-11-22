"""Pytest configuration and fixtures for chuk-mcp-open-meteo tests."""

import asyncio

import pytest


@pytest.fixture
def london_coords():
    """Coordinates for London, UK."""
    return {"latitude": 51.5072, "longitude": -0.1276}


@pytest.fixture
def new_york_coords():
    """Coordinates for New York City, USA."""
    return {"latitude": 40.7128, "longitude": -74.0060}


@pytest.fixture
def tokyo_coords():
    """Coordinates for Tokyo, Japan."""
    return {"latitude": 35.6762, "longitude": 139.6503}


@pytest.fixture
def sample_date_range():
    """Sample date range for historical weather tests."""
    return {"start_date": "2024-01-01", "end_date": "2024-01-07"}


@pytest.fixture
async def retry_on_network_error():
    """Fixture that provides retry logic for network operations."""

    async def _retry(coro_func, max_retries=3, initial_delay=1.0):
        """Retry an async function with exponential backoff on network errors."""
        for attempt in range(max_retries):
            try:
                return await coro_func()
            except Exception as e:
                # Check if it's a network-related error
                error_str = str(type(e).__name__).lower()
                if any(
                    keyword in error_str
                    for keyword in ["connect", "timeout", "network", "tls", "ssl"]
                ):
                    if attempt < max_retries - 1:
                        delay = initial_delay * (2**attempt)
                        print(
                            f"Network error on attempt {attempt + 1}/{max_retries}, retrying in {delay}s: {e}"
                        )
                        await asyncio.sleep(delay)
                        continue
                # Re-raise if not a network error or out of retries
                raise
        raise Exception(f"Failed after {max_retries} attempts")

    return _retry
