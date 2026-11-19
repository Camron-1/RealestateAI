
from services.repliers import get_listings
from services.overpass import get_closest_places
from services.ranking import calculate_home_score


def search_homes(
    city,
    state=None,
    max_price=None,
    property_type=None,
    min_bedrooms=None,
    min_bathrooms=None,
    wants_hospital=False,
    wants_school=False,
    wants_park=False,
    wants_dog_park=False,
    wants_playground=False,
    bedroom_mode="minimum",
    bathroom_mode="minimum"
):
    """
    Search homes, enforce price and room requirements,
    retrieve nearby amenities, and calculate match scores.
    """

    # -----------------------------------
    # Step 1: Retrieve homes from Repliers
    # -----------------------------------

    results = get_listings(
        city=city,
        state=state,
        max_price=max_price,
        property_type=property_type,
        min_bedrooms=(
            min_bedrooms
            if bedroom_mode != "maximum"
            else None
        ),
        min_bathrooms=(
            min_bathrooms
            if bathroom_mode != "maximum"
            else None
        ),
        results_per_page=100
    )

    listings = results.get("listings", [])

    print("TOTAL HOMES FROM REPLIERS:", len(listings))

    if not listings:
        return []

    # -----------------------------------
    # Step 2: Helper functions
    # -----------------------------------

    def get_room_count(home, room_type):
        details = home.get("details") or {}

        if room_type == "bedrooms":
            possible_values = [
                details.get("numBedrooms"),
                details.get("bedrooms"),
                home.get("bedrooms"),
                home.get("numBedrooms")
            ]
        else:
            possible_values = [
                details.get("numBathrooms"),
                details.get("numBathroomsTotal"),
                details.get("bathrooms"),
                home.get("bathrooms"),
                home.get("numBathrooms")
            ]

        for value in possible_values:
            if value is not None:
                try:
                    return float(value)
                except (TypeError, ValueError):
                    continue

        return None

    def matches_room_count(actual, requested, mode):
        if requested is None:
            return True

        if actual is None:
            return False

        requested = float(requested)

        if mode == "exact":
            return actual == requested

        if mode == "minimum":
            return actual >= requested

        if mode == "maximum":
            return actual <= requested

        return False

    def get_price(home):
        for key in ["price", "listPrice"]:
            value = home.get(key)

            if value is not None:
                try:
                    return float(
                        str(value).replace(",", "").replace("$", "")
                    )
                except (TypeError, ValueError):
                    continue

        return None

    def has_nearby_amenity(nearby, amenity):
        """
        get_closest_places() returns a dictionary
        keyed by amenity type, for example:
        {
            "school": {...},
            "park": {...}
        }
        """

        if not isinstance(nearby, dict):
            return False

        place = nearby.get(amenity)

        if not isinstance(place, dict):
            return False

        distance = place.get("distance_miles")

        if distance is None:
            return False

        try:
            return float(distance) >= 0
        except (TypeError, ValueError):
            return False

    # -----------------------------------
    # Step 3: Apply room and price filters
    # -----------------------------------

    filtered_listings = []

    for home in listings:
        bedrooms = get_room_count(home, "bedrooms")
        bathrooms = get_room_count(home, "bathrooms")
        price = get_price(home)

        if not matches_room_count(
            bedrooms,
            min_bedrooms,
            bedroom_mode
        ):
            continue

        if not matches_room_count(
            bathrooms,
            min_bathrooms,
            bathroom_mode
        ):
            continue

        if max_price is not None:
            if price is None or price > float(max_price):
                continue

        filtered_listings.append(home)

    print(
        "HOMES AFTER PRICE AND ROOM FILTER:",
        len(filtered_listings)
    )

    if not filtered_listings:
        return []

    # -----------------------------------
    # Step 4: Determine required amenities
    # -----------------------------------

    requested_amenities = {
        "hospital": wants_hospital,
        "school": wants_school,
        "park": wants_park,
        "dog_park": wants_dog_park,
        "playground": wants_playground
    }

    required_amenities = [
        amenity
        for amenity, selected in requested_amenities.items()
        if selected
    ]

    print("REQUIRED AMENITIES:", required_amenities)

    # -----------------------------------
    # Step 5: Retrieve amenities and score
    # -----------------------------------

    matching_homes = []

    # When amenities are required, examine more candidates.
    # Otherwise, check the first 10 matching homes.
    candidates = filtered_listings[:10]
    

    for home in candidates:
        latitude = home.get("latitude")
        longitude = home.get("longitude")

        # Repliers may sometimes provide coordinates
        # inside the map object.
        map_data = home.get("map") or {}

        if latitude is None:
            latitude = map_data.get("latitude")

        if longitude is None:
            longitude = map_data.get("longitude")

        home["nearby"] = {}

        # -----------------------------------
        # Retrieve nearby amenities
        # -----------------------------------

        if latitude is None or longitude is None:
            home["nearby_status"] = "Location unavailable"

            print("HOME LOCATION UNAVAILABLE")

            if required_amenities:
                continue

        else:
            print("HOME COORDINATES:", latitude, longitude)

            try:
                nearby_places = get_closest_places(
                    latitude=latitude,
                    longitude=longitude
                )

                home["nearby"] = nearby_places
                home.pop("nearby_status", None)

                # DEBUG: Inspect actual Overpass response.
                print("NEARBY PLACES:", nearby_places)
                print(
                    "NEARBY TYPES:",
                    list(nearby_places.keys())
                )

            except Exception as error:
                print("OVERPASS ERROR:", error)

                home["nearby_status"] = (
                    "Nearby places temporarily unavailable"
                )

                if required_amenities:
                    continue

        # -----------------------------------
        # Enforce selected amenity filters
        # -----------------------------------

        if required_amenities:
            if not all(
                has_nearby_amenity(
                    home["nearby"],
                    amenity
                )
                for amenity in required_amenities
            ):
                print(
                    "HOME SKIPPED - MISSING REQUIRED AMENITY"
                )
                continue

        # -----------------------------------
        # Calculate AI match score
        # -----------------------------------

        if "nearby_status" not in home:
            home["match_score"] = calculate_home_score(
                home=home,
                max_price=max_price,
                min_bedrooms=min_bedrooms,
                min_bathrooms=min_bathrooms,
                wants_hospital=wants_hospital,
                wants_school=wants_school,
                wants_park=wants_park,
                wants_dog_park=wants_dog_park,
                wants_playground=wants_playground
            )

        else:
            # Score is unknown when nearby data could not
            # be retrieved. Don't invent a percentage.
            home["match_score"] = None

        print("HOME MATCH SCORE:", home["match_score"])

        matching_homes.append(home)

    # -----------------------------------
    # Step 6: Sort by match score
    # -----------------------------------

    matching_homes.sort(
        key=lambda home: home.get("match_score") or 0,
        reverse=True
    )

    final_homes = matching_homes[:10]

    print("FINAL HOMES RETURNED:", len(final_homes))

    return final_homes
