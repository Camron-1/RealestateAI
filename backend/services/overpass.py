import requests
from services.data_structure import normalize_place
from services.distance import calculate_distance
OVERPASS_URL = "https://overpass-api.de/api/interpreter"


def get_nearby_places(latitude, longitude, radius=5000):

    query = f"""
    [out:json];
    (
        nwr["amenity"="hospital"](around:{radius},{latitude},{longitude});
        nwr["amenity"="school"](around:{radius},{latitude},{longitude});
        nwr["leisure"="park"](around:{radius},{latitude},{longitude});
        nwr["leisure"="dog_park"](around:{radius},{latitude},{longitude});
        nwr["leisure"="playground"](around:{radius},{latitude},{longitude});
    );
    out center;
    """

    headers = {
        "User-Agent": "RealestateAI/1.0"
    }

    response = requests.post(
        OVERPASS_URL,
        data={"data": query},
        headers=headers
    )

    response.raise_for_status()
    data=response.json()
    places=data.get("elements", [])
    normalized_places = []

    for place in places:
        normalized_place = normalize_place(place)
        place_latitude = normalized_place.get("latitude")
        place_longitude = normalized_place.get("longitude")
        distance=calculate_distance(
            latitude,
            longitude,
            place_latitude,
            place_longitude
        )
        normalized_place["distance_Miles"] = distance
        normalized_places.append(normalized_place)

    return normalized_places