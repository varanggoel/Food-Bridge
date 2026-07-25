"""Geocoding via OpenStreetMap Nominatim (free, no API key required).

Used only to convert an address/city string into lat/lon ONE TIME when a
donation or NGO is created. This is a lookup, not a live map UI, so it stays
within the MVP scope (no maps/analytics).
"""
import requests
from math import radians, sin, cos, sqrt, atan2
from app.config import get_logger

logger = get_logger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"


def geocode_address(address: str, city: str) -> tuple[float, float] | None:
    """Returns (lat, lon) or None if geocoding fails."""
    query = f"{address}, {city}, India"
    try:
        resp = requests.get(
            NOMINATIM_URL,
            params={"q": query, "format": "json", "limit": 1},
            headers={"User-Agent": "FoodBridgeIndia/1.0"},
            timeout=8,
        )
        resp.raise_for_status()
        results = resp.json()
        if not results:
            # Fallback: try city only
            resp2 = requests.get(
                NOMINATIM_URL,
                params={"q": f"{city}, India", "format": "json", "limit": 1},
                headers={"User-Agent": "FoodBridgeIndia/1.0"},
                timeout=8,
            )
            resp2.raise_for_status()
            results = resp2.json()
            if not results:
                logger.warning(f"Geocoding failed for '{query}'")
                return None
        lat = float(results[0]["lat"])
        lon = float(results[0]["lon"])
        return (lat, lon)
    except Exception as e:
        logger.error(f"Geocoding error for '{query}': {e}")
        return None


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))
