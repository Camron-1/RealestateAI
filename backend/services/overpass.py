import requests
import time

from services.data_structure import normalize_place
from services.distance import calculate_distance


# Overpass API endpoint used to search OpenStreetMap data
# for places such as hospitals, schools, parks, and playgrounds.
OVERPASS_URL = "https://overpass-api.de/api/interpreter"


# Stores previous nearby-place searches in memory.
# This prevents us from repeatedly sending the same request
# to Overpass for the same location and radius.
nearby_cache = {}


def get_nearby_places(latitude, longitude, radius=16000):
    """
    Finds nearby amenities around a home's latitude and longitude.

    The function searches OpenStreetMap through the Overpass API,
    normalizes the returned place data, calculates the distance
    from the home to each place, and returns the finished list.

    The default search radius is 16,000 meters, which is
    approximately 10 miles.
    """

    # Create a unique cache key using the home's coordinates
    # and search radius.
    cache_key = (latitude, longitude, radius)

    # If we have already searched this exact location and radius,
    # return the saved results instead of calling Overpass again.
    if cache_key in nearby_cache:
        return nearby_cache[cache_key]

    # Build the Overpass query.
    #
    # nwr means search OpenStreetMap nodes, ways, and relations.
    # "around" searches within the specified radius of the home.
    #
    # We currently search for:
    # - hospitals
    # - schools
    # - parks
    # - dog parks
    # - playgrounds
    #
    # "out center" gives us coordinates for larger map objects
    # such as ways and relations.
    query = f"""
    [out:json][timeout:25];
    (
        nwr["amenity"="hospital"](around:{radius},{latitude},{longitude});
        nwr["amenity"="school"](around:{radius},{latitude},{longitude});
        nwr["leisure"="park"](around:{radius},{latitude},{longitude});
        nwr["leisure"="dog_park"](around:{radius},{latitude},{longitude});
        nwr["leisure"="playground"](around:{radius},{latitude},{longitude});
    );
    out center;
    """

    # Identify our application when sending requests to Overpass.
    headers = {
        "User-Agent": "RealestateAI/1.0"
    }

    # Overpass is a public service and can occasionally be busy
    # or temporarily unavailable. Try the request up to 3 times
    # before allowing the error to be passed back to our application.
    for attempt in range(3):
        try:
            response = requests.post(
                OVERPASS_URL,
                data={"data": query},
                headers=headers,
                timeout=30
            )

            # Raise an error if Overpass returned an unsuccessful
            # HTTP status code.
            response.raise_for_status()

            # The request worked, so we do not need another attempt.
            break

        except requests.exceptions.RequestException:

            # If the third attempt also fails, stop retrying
            # and pass the error back to the calling function.
            if attempt == 2:
                raise

            # Wait 3 seconds before trying Overpass again.
            time.sleep(3)

    # Convert the JSON response into a Python dictionary.
    data = response.json()

    # Overpass stores the places it found inside "elements".
    # Use an empty list if no places were found.
    places = data.get("elements", [])

    normalized_places = []

    # Go through every place returned by Overpass.
    for place in places:

        # Convert the raw OpenStreetMap place into the simpler
        # structure used throughout our application.
        normalized_place = normalize_place(place)

        place_latitude = normalized_place.get("latitude")
        place_longitude = normalized_place.get("longitude")

        # We need coordinates for both the home and place
        # in order to calculate the distance between them.
        if place_latitude is not None and place_longitude is not None:

            # Calculate the straight-line distance from the home
            # to this nearby place in miles.
            distance = calculate_distance(
                latitude,
                longitude,
                place_latitude,
                place_longitude
            )

            # Add the calculated distance to the place's information.
            normalized_place["distance_miles"] = distance

        normalized_places.append(normalized_place)

    # Save the completed search in the cache so another request
    # for this same location does not have to call Overpass again.
    nearby_cache[cache_key] = normalized_places

    return normalized_places


def get_closest_places(latitude, longitude, radius=16000):
    """
    Finds the closest place of each amenity type around a home.

    Instead of returning every hospital, school, park, etc.,
    this function keeps only the closest one of each type.
    """

    # Get all nearby places around the home.
    places = get_nearby_places(
        latitude=latitude,
        longitude=longitude,
        radius=radius
    )

    # This dictionary will eventually contain one closest place
    # for each type, such as hospital, school, park, or playground.
    closest_places = {}

    for place in places:

        place_type = place.get("type")
        distance = place.get("distance_miles")

        # Skip places that do not have a type or calculated distance.
        if place_type is None or distance is None:
            continue

        # If this is the first place we have found of this type,
        # temporarily consider it the closest one.
        if place_type not in closest_places:
            closest_places[place_type] = place

        # If we already found this type, replace it only when
        # the new place is closer to the home.
        elif distance < closest_places[place_type]["distance_miles"]:
            closest_places[place_type] = place

    # Return only the closest location for each amenity type.
    return closest_places