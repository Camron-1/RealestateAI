# Import the functions needed to:
# 1. Get home listings from Repliers
# 2. Find nearby places using Overpass
# 3. Calculate how well each home matches the user's preferences
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
    wants_playground=False
):
    """
    Searches for homes and ranks them based on the user's preferences.

    First, Repliers is used to find homes that match basic requirements
    such as location, price, bedrooms, and bathrooms.

    Then, Overpass is used to find nearby amenities for each home.

    Finally, each home receives a match score based on the preferences
    the user requested.
    """

    # Search Repliers for homes that match the user's basic filters.
    # These are the "hard" filters because Repliers uses them to
    # determine which homes should be returned.
    results = get_listings(
        city=city,
        state=state,
        max_price=max_price,
        property_type=property_type,
        min_bedrooms=min_bedrooms,
        min_bathrooms=min_bathrooms,
        results_per_page=10
    )

    # Get just the list of homes from the Repliers response.
    # If "listings" does not exist, use an empty list instead.
    listings = results.get("listings", [])

    # If Repliers did not find any matching homes,
    # there is nothing else to process, so return an empty list.
    if not listings:
        return []

    # Go through every home returned by Repliers so we can
    # find nearby places and calculate its match score.
    for home in listings:

        # Get the home's coordinates.
        # These coordinates are needed to search for nearby amenities.
        latitude = home.get("latitude")
        longitude = home.get("longitude")

        # If Repliers does not provide coordinates for this home,
        # Overpass cannot search for places around it.
        if latitude is None or longitude is None:
            home["nearby"] = {}
            home["nearby_status"] = "Location unavailable"

        else:
            try:
                # Search for the closest hospital, school, park,
                # dog park, and playground around this home.
                nearby_places = get_closest_places(
                    latitude=latitude,
                    longitude=longitude
                )

                # Add the nearby-place information directly
                # to this home's data.
                home["nearby"] = nearby_places

            except Exception:
                # Overpass is a public API and may occasionally fail.
                # Instead of causing the entire home search to fail,
                # return the home without nearby-place information.
                home["nearby"] = {}
                home["nearby_status"] = (
                    "Nearby places temporarily unavailable"
                )

        # Only calculate a match score when nearby-place information
        # was successfully retrieved.
        if "nearby_status" not in home:

            # The ranking function checks the user's requested
            # preferences and gives the home a percentage match score.
            home["match_score"] = calculate_home_score(
                home=home,
                max_price=max_price,
                wants_hospital=wants_hospital,
                wants_school=wants_school,
                wants_park=wants_park,
                wants_dog_park=wants_dog_park,
                wants_playground=wants_playground
            )

        else:
            # If nearby-place information failed, do not give the home
            # a potentially misleading match percentage.
            home["match_score"] = None

    # Sort the homes from highest match score to lowest.
    # "or 0" makes homes without a match score sort toward the bottom.
    # reverse=True means the highest scores appear first.
    listings.sort(
        key=lambda home: home.get("match_score") or 0,
        reverse=True
    )

    # Return the finished list of homes with nearby-place
    # information and match scores included.
    return listings