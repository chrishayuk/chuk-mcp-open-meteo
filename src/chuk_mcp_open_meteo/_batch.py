"""Shared batch fetch helper for coordinate-based Open-Meteo APIs."""

from typing import Any, TypeVar

import httpx
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


async def batch_fetch(
    api_url: str,
    params: dict[str, Any],
    item_model: type[T],
    timeout: float = 60.0,
) -> list[T]:
    """Fetch data for multiple locations from an Open-Meteo API endpoint.

    Open-Meteo APIs accept comma-separated latitude/longitude values and return
    either a JSON array (multiple locations) or a single object (one location).
    This helper handles both cases and wraps each result in the given Pydantic model.

    Args:
        api_url: The Open-Meteo API endpoint URL.
        params: Query parameters dict (must include 'latitude' and 'longitude'
                as comma-separated strings).
        item_model: The Pydantic model class to wrap each result in.
        timeout: HTTP request timeout in seconds.

    Returns:
        List of item_model instances, one per location.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(api_url, params=params, timeout=timeout)
        response.raise_for_status()
        data = response.json()

    if isinstance(data, list):
        return [item_model(**item) for item in data]
    else:
        return [item_model(**data)]
