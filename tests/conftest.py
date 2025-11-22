"""Pytest configuration and fixtures for chuk-mcp-open-meteo tests."""

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
