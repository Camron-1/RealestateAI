import os
import requests

from dotenv import load_dotenv
from services.data_structure import normalize_listing


# Load variables from the .env file.
# This allows us to securely access the Repliers API key
# without putting the actual key directly in the code.
load_dotenv()

REPLIERS_API_KEY = os.getenv("REPLIERS_API_KEY")

# Repliers endpoint used to search for real estate listings.
REPLIERS_URL = "https://api.repliers.io/listings"


def get_listings(
    city=None,
    state=None,
    min_price=None,
    max_price=None,
    min_bedrooms=None,
    min_bathrooms=None,
    property_type=None,
    page=1,
    results_per_page=10,
    sort_by=None
):
    """
    Searches the Repliers API for homes using the filters provided.

    Most filters are optional. If a filter is None, it will not be
    included in the request.

    The listings returned by Repliers are normalized before being
    returned so the rest of our application has a consistent
    structure to work with.
    """

    # Headers sent with the API request.
    # Repliers requires our API key to verify that we are
    # authorized to access their listing data.
    headers = {
        "REPLIERS-API-KEY": REPLIERS_API_KEY,
        "Content-Type": "application/json"
    }

    # These parameters are included with every listing search.
    # "A" means we only want active listings.
    # "sale" means we are searching for homes for sale.
    # pageNum and resultsPerPage control pagination.
    params = {
        "status": "A",
        "type": "sale",
        "pageNum": page,
        "resultsPerPage": results_per_page
    }

    # Add a city to the search only if the user provided one.
    if city is not None:
        params["city"] = city

    # Add a state to the search only if the user provided one.
    if state is not None:
        params["state"] = state

    # Set the lowest acceptable home price if one was provided.
    if min_price is not None:
        params["minPrice"] = min_price

    # Set the highest acceptable home price if one was provided.
    if max_price is not None:
        params["maxPrice"] = max_price

    # Only return homes with at least this many bedrooms.
    if min_bedrooms is not None:
        params["minBedrooms"] = min_bedrooms

    # Only return homes with at least this many bathrooms.
    if min_bathrooms is not None:
        params["minBaths"] = min_bathrooms

    # Filter by property type if the user specifically requested one,
    # such as Residential, Condo, etc.
    if property_type is not None:
        params["propertyType"] = property_type

    # Add sorting only when a sorting option was provided.
    # For example, this can be used to sort homes by price.
    if sort_by is not None:
        params["sortBy"] = sort_by

    # Send a GET request to Repliers with our headers and search filters.
    # timeout=30 prevents the application from waiting forever
    # if Repliers does not respond.
    response = requests.get(
        REPLIERS_URL,
        headers=headers,
        params=params,
        timeout=30
    )

    # If Repliers returns an HTTP error such as 400, 401, or 500,
    # raise an exception instead of continuing with bad data.
    response.raise_for_status()

    # Convert the JSON response from Repliers into a Python dictionary.
    data = response.json()

    # Repliers stores the actual home results inside the "listings" field.
    # If no listings were returned, use an empty list instead.
    listings = data.get("listings", [])

    # This list will contain our cleaned versions of the Repliers listings.
    normalized_listings = []

    # Repliers returns a lot of data for each property.
    # normalize_listing() keeps the fields our application needs
    # and puts them into a consistent structure.
    for listing in listings:
        normalized_listing = normalize_listing(listing)

        normalized_listings.append(
            normalized_listing
        )

    # Return both the pagination information and our cleaned listings.
    # This is the structure that the rest of our backend will work with.
    return {
        "page": data.get("page"),
        "totalPages": data.get("numPages"),
        "pageSize": data.get("pageSize"),
        "totalListings": data.get("count"),
        "listings": normalized_listings
    }