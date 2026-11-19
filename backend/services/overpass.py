
import os
import time
import requests

from dotenv import load_dotenv
from services.distance import calculate_distance

load_dotenv()

GEOAPIFY_URL = "https://api.geoapify.com/v2/places"

# Geoapify's documented categories.
CATEGORIES = {
    "hospital": "healthcare.hospital",
    "school": "education.school",
    "park": "leisure.park",
    "playground": "leisure.playground",
}

# In-memory cache: expires after one hour.
nearby_cache = {}
CACHE_SECONDS = 3600


def get_nearby_places(latitude, longitude, radius=5000):
    """
    Retrieve nearby amenities using Geoapify.

    Returns a list of normalized places with:
    name, type, latitude, longitude, distance_miles.
    """

    api_key = os.getenv("GEOAPIFY_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEOAPIFY_API_KEY is missing from your .env file"
        )

    latitude = float(latitude)
    longitude = float(longitude)
    radius = int(radius)

    cache_key = (
        round(latitude, 5),
        round(longitude, 5),
        radius
    )

    cached = nearby_cache.get(cache_key)

    if cached and time.time() - cached["timestamp"] < CACHE_SECONDS:
        print("USING CACHED GEOAPIFY AMENITIES")
        return cached["places"]

    params = {
        "categories": ",".join(CATEGORIES.values()),
        "filter": f"circle:{longitude},{latitude},{radius}",
        "bias": f"proximity:{longitude},{latitude}",
        "limit": 500,
        "apiKey": api_key,
    }

    print("SEARCHING GEOAPIFY:", latitude, longitude)

    try:
        response = requests.get(
            GEOAPIFY_URL,
            params=params,
            timeout=(5, 15)
        )

        response.raise_for_status()
        data = response.json()

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Geoapify request failed: {error}"
        ) from error

    places = []
    seen = set()

    for feature in data.get("features", []):
        properties = feature.get("properties") or {}
        geometry = feature.get("geometry") or {}

        coordinates = geometry.get("coordinates") or []

        if len(coordinates) < 2:
            continue

        place_lon = float(coordinates[0])
        place_lat = float(coordinates[1])

        categories = properties.get("categories") or []
        name = properties.get("name") or properties.get("formatted")

        if not name:
            name = "Unnamed place"

        place_types = []

        for place_type, category in CATEGORIES.items():
            if any(
                item == category or item.startswith(category + ".")
                for item in categories
            ):
                place_types.append(place_type)

        # Geoapify does not document a dedicated dog-park
        # category. Recognize clearly named dog parks.
        if any(
            phrase in name.lower()
            for phrase in ("dog park", "dog run", "off-leash dog")
        ):
            place_types.append("dog_park")

        distance = calculate_distance(
            latitude,
            longitude,
            place_lat,
            place_lon
        )

        for place_type in set(place_types):
            unique_key = (
                properties.get("place_id")
                or (place_lat, place_lon),
                place_type
            )

            if unique_key in seen:
                continue

            seen.add(unique_key)

            places.append({
                "name": name,
                "type": place_type,
                "latitude": place_lat,
                "longitude": place_lon,
                "distance_miles": round(distance, 2),
                "address": properties.get("formatted"),
            })

    nearby_cache[cache_key] = {
        "timestamp": time.time(),
        "places": places
    }

    print("GEOAPIFY AMENITIES FOUND:", len(places))

    return places


def get_closest_places(latitude, longitude, radius=5000):
    """
    Return the closest place for each amenity type.
    Compatible with the existing home_search.py.
    """

    places = get_nearby_places(
        latitude=latitude,
        longitude=longitude,
        radius=radius
    )

    closest_places = {}

    for place in places:
        place_type = place["type"]

        if (
            place_type not in closest_places
            or place["distance_miles"]
            < closest_places[place_type]["distance_miles"]
        ):
            closest_places[place_type] = place

    return closest_places
