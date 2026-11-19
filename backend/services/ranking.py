
def calculate_home_score(
    home,
    max_price=None,
    wants_hospital=False,
    wants_school=False,
    wants_park=False,
    wants_dog_park=False,
    wants_playground=False,
    min_bedrooms=None,
    min_bathrooms=None,
):
    """
    Calculate how closely a home matches the user's preferences.

    Scoring considers:
    - Bedrooms
    - Bathrooms
    - Maximum price
    - Nearby amenities

    Only preferences requested by the user affect the score.
    """

    score = 0
    possible_score = 0

    # -----------------------------------
    # Bedroom scoring
    # -----------------------------------

    if min_bedrooms is not None:
        possible_score += 20

        home_bedrooms = home.get("bedrooms")

        if home_bedrooms is not None:
            if home_bedrooms >= min_bedrooms:
                score += 20

            elif home_bedrooms == min_bedrooms - 1:
                score += 10

    # -----------------------------------
    # Bathroom scoring
    # -----------------------------------

    if min_bathrooms is not None:
        possible_score += 20

        home_bathrooms = home.get("bathrooms")

        if home_bathrooms is not None:
            if home_bathrooms >= min_bathrooms:
                score += 20

            elif home_bathrooms >= min_bathrooms - 1:
                score += 10

    # -----------------------------------
    # Price scoring
    # -----------------------------------

    if max_price is not None and max_price > 0:
        possible_score += 20

        price = home.get("price")

        if price is not None:
            if price <= max_price:
                score += 20

            elif price <= max_price * 1.05:
                score += 15

            elif price <= max_price * 1.10:
                score += 10

    # -----------------------------------
    # Nearby amenity scoring
    # -----------------------------------

    nearby = home.get("nearby", {}) or {}

    preferences = {
        "hospital": wants_hospital,
        "school": wants_school,
        "park": wants_park,
        "dog_park": wants_dog_park,
        "playground": wants_playground,
    }

    for place_type, wanted in preferences.items():
        if not wanted:
            continue

        possible_score += 20

        place = nearby.get(place_type)

        if place is None:
            continue

        distance = place.get("distance_miles")

        if distance is None:
            continue

        if distance <= 1:
            score += 20

        elif distance <= 3:
            score += 16

        elif distance <= 5:
            score += 12

        elif distance <= 7:
            score += 8

        elif distance <= 10:
            score += 4

    # -----------------------------------
    # Final percentage
    # -----------------------------------

    if possible_score == 0:
        return None

    percentage = (score / possible_score) * 100

    return round(percentage)
