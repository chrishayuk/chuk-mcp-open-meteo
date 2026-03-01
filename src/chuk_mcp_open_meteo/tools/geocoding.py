"""Geocoding tools — single and batch."""

import asyncio

import httpx
from chuk_mcp_server import tool

from .._constants import GEOCODING_API
from ..models import (
    BatchGeocodingItem,
    BatchGeocodingResponse,
    GeocodingResponse,
)


@tool
async def geocode_location(
    name: str,
    count: int = 10,
    language: str = "en",
    format: str = "json",
) -> GeocodingResponse:
    """Convert location names to coordinates and get detailed geographic information.

    Use this tool FIRST before calling weather tools to get accurate coordinates for any location.
    Searches worldwide database of cities, towns, and places with comprehensive metadata.

    Args:
        name: Location name to search for. Can be:
            - City name: "London", "Tokyo", "New York"
            - City with country: "Paris, France", "Portland, Oregon"
            - Region or landmark: "Cornwall", "Lake Tahoe"
            - Address or place: "Times Square", "Big Ben"
        count: Maximum number of results to return (1-100). Default is 10.
            Use 1 if you're confident about the location (e.g., "London, UK")
            Use 5-10 for ambiguous names (e.g., "Paris" - could be France, Texas, etc.)
        language: Language code for result names. Options: "en" (English, default), "de" (German),
            "fr" (French), "es" (Spanish), "it" (Italian), "pt" (Portuguese), etc.
        format: Response format. Always use "json" (default).

    Returns:
        GeocodingResponse: A Pydantic model containing:
            - results: List of matching locations, each with:
                - name: Location name
                - latitude, longitude: Coordinates (use these for weather tools!)
                - country, country_code: Country information
                - timezone: IANA timezone (e.g., "Europe/London")
                - elevation: Meters above sea level
                - population: Population (if available)
                - admin1, admin2: Administrative divisions (state, county, etc.)
                - feature_code: Type of place (PPLC=capital, PPL=populated place, etc.)

    Tips for LLMs:
        - ALWAYS geocode location names before requesting weather data
        - Results are sorted by relevance (population, importance)
        - First result is usually what users mean for well-known cities
        - For ambiguous names, check country/admin divisions to pick the right one
        - Use the exact latitude/longitude from results in weather API calls
        - Timezone from geocoding can be passed to weather APIs for local time
        - **CRITICAL**: If no results found, IMMEDIATELY retry with simpler search terms!
          The API works best with just city names (e.g., "Portland" not "Portland Harbor" or "Portland, Maine")
          WORKFLOW: If "City, Region" fails → AUTOMATICALLY try just "City" → filter by admin1/admin2/country
          DO NOT ask the user - just retry automatically with the simpler name!
        - If still no results after retry: try even simpler terms or use nearest known location
        - Common pattern: "Harbor Name" fails → retry just the city name → filter by region/country

    Example:
        # Find London coordinates
        locations = await geocode_location("London", count=1)
        london = locations.results[0]
        # Use coordinates for weather: london.latitude, london.longitude

        # Handle ambiguous names
        locations = await geocode_location("Paris", count=5)
        # results[0] = Paris, France (population 2.1M)
        # results[1] = Paris, Texas (population 25K)
        # Pick based on context or ask user

        # If "City, Region" returns no results, try just "City"
        locations = await geocode_location("Portland, Maine", count=5)
        if not locations.results:
            # Try simpler search
            locations = await geocode_location("Portland", count=5)
            # Filter by country_code='US' and admin1='Maine' to get the right one
            portland = next(r for r in locations.results if r.country_code == 'US' and r.admin1 == 'Maine')
    """
    params = {
        "name": name,
        "count": count,
        "language": language,
        "format": format,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(GEOCODING_API, params=params, timeout=30.0)
        response.raise_for_status()
        data = response.json()

    return GeocodingResponse(**data)


@tool
async def batch_geocode_locations(
    names: str,
    count: int = 1,
    language: str = "en",
) -> BatchGeocodingResponse:
    """Geocode multiple location names to coordinates in a single call.

    Use this tool instead of calling geocode_location repeatedly when you need
    coordinates for multiple locations (e.g., "weather across the UK",
    "compare temperatures in European capitals").

    This tool makes all geocoding requests concurrently, dramatically reducing
    latency compared to sequential calls. For N locations, this completes in
    roughly the time of 1 request instead of N sequential requests.

    Args:
        names: Comma-separated list of location names to geocode.
            Examples:
                - "London,Paris,Berlin,Madrid,Rome"
                - "New York,Los Angeles,Chicago,Houston"
                - "Tokyo,Seoul,Beijing,Shanghai"
            Each name is searched independently. Whitespace around commas is trimmed.
            Maximum recommended: 50 locations per call.
        count: Maximum number of results per location (1-10). Default is 1.
            Use 1 when you know the exact locations (most common for batch).
            Use 3-5 for ambiguous names where you need to pick the right match.
        language: Language code for result names. Default is "en".

    Returns:
        BatchGeocodingResponse: Contains:
            - results: List of BatchGeocodingItem, one per input location, in order.
              Each item has: query (original name), found (bool), results (list), error (str or None)
            - total_queries: How many locations were searched
            - successful: How many returned results
            - failed: How many returned no results or had errors

    Tips for LLMs:
        - Use this FIRST when a user asks about weather in multiple places
        - After getting coordinates, pass them to batch_get_weather_forecasts
        - Partial failures are normal - some location names may not be found
        - Check the 'found' field on each item to identify failures
        - For failed items, try simpler search terms (just city name without region)
        - The results are in the SAME ORDER as the input names

    Example:
        # Geocode 5 UK cities at once
        batch = await batch_geocode_locations("London,Manchester,Edinburgh,Cardiff,Belfast")
        # Extract coordinates for found locations
        coords = [(r.results[0].latitude, r.results[0].longitude)
                  for r in batch.results if r.found]
    """
    location_names = [name.strip() for name in names.split(",") if name.strip()]

    if not location_names:
        return BatchGeocodingResponse(results=[], total_queries=0, successful=0, failed=0)

    semaphore = asyncio.Semaphore(10)

    async def _geocode_one(client: httpx.AsyncClient, name: str) -> BatchGeocodingItem:
        async with semaphore:
            try:
                params = {
                    "name": name,
                    "count": count,
                    "language": language,
                    "format": "json",
                }
                response = await client.get(GEOCODING_API, params=params, timeout=30.0)
                response.raise_for_status()
                data = response.json()

                geo_response = GeocodingResponse(**data)
                has_results = geo_response.results is not None and len(geo_response.results) > 0
                return BatchGeocodingItem(
                    query=name,
                    found=has_results,
                    results=geo_response.results if has_results else None,
                    error=None,
                )
            except Exception as e:
                return BatchGeocodingItem(
                    query=name,
                    found=False,
                    results=None,
                    error=f"{type(e).__name__}: {e}",
                )

    async with httpx.AsyncClient() as client:
        items = await asyncio.gather(*[_geocode_one(client, name) for name in location_names])

    successful = sum(1 for item in items if item.found)

    return BatchGeocodingResponse(
        results=list(items),
        total_queries=len(location_names),
        successful=successful,
        failed=len(location_names) - successful,
    )
