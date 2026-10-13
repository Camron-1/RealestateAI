def calculate_home_score(
    home,
    max_price=None,
    wants_hospital=False,
    wants_school=False,
    wants_park=False,
    wants_dog_park=False,
    wants_playground=False
):
    """
    Calculates how well a home matches the user's preferences.

    The home receives points for meeting the user's maximum price
    and for having requested amenities nearby.

    Amenities that are closer to the home receive more points.

    The final score is returned as a percentage.
    """

    # Points the home has earned.
    score = 0

    # Maximum number of points the home could earn
    # based only on preferences the user requested.
    possible_score = 0


    # -----------------------------------
    # Price scoring
    # -----------------------------------

    # Only include price in the score if the user
    # actually provided a maximum price.
    if max_price is not None:

        possible_score += 20

        price = home.get("price")

        # Give the home all 20 price points if it
        # is at or below the user's maximum price.
        if price is not None and price <= max_price:
            score += 20


    # -----------------------------------
    # Nearby amenity scoring
    # -----------------------------------

    # Get the nearby places that were added to the home
    # by our Overpass search.
    nearby = home.get("nearby", {})

    # Connect each type of nearby place with whether
    # the user actually requested that type of place.
    preferences = {
        "hospital": wants_hospital,
        "school": wants_school,
        "park": wants_park,
        "dog_park": wants_dog_park,
        "playground": wants_playground
    }

    # Check each possible nearby-place preference.
    for place_type, wanted in preferences.items():

        # If the user did not request this type of place,
        # it should not affect the home's match score.
        if not wanted:
            continue

        # Each requested amenity is worth up to 20 points.
        possible_score += 20

        # Get the closest place of this type.
        place = nearby.get(place_type)

        # If no nearby place of this type was found,
        # the home receives 0 points for this preference.
        if place is None:
            continue

        distance = place.get("distance_miles")

        # We cannot score the place if its distance
        # could not be calculated.
        if distance is None:
            continue


        # -----------------------------------
        # Distance scoring
        # -----------------------------------

        # Closer amenities receive more points.
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
    # Calculate final percentage
    # -----------------------------------

    # If the user did not provide any preferences that
    # can be scored, avoid dividing by zero.
    if possible_score == 0:
        return 0

    # Convert the earned points into a percentage.
    percentage = (score / possible_score) * 100

    # Return the percentage rounded to the nearest whole number.
    return round(percentage)