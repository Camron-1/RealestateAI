import os
import requests
from services.data_structure import normalize_listing

from dotenv import load_dotenv


load_dotenv()

REPLIERS_API_KEY = os.getenv("REPLIERS_API_KEY")

REPLIERS_URL = "https://api.repliers.io/listings"


def get_listings(
    city=None,
    min_price=None,
    max_price=None,
    min_bedrooms=None,
    min_bathrooms=None,
    page=1,
    results_per_page=10,
    sort_by=None
):


    headers = {
        "REPLIERS-API-KEY": REPLIERS_API_KEY,
        "Content-Type": "application/json"
    }

    params = {
        "status": "A",
        "type": "sale",
        "pageNum": page,
        "resultsPerPage": results_per_page,
        "sortBy": sort_by
    }
    sort_by = "listPriceAsc"

    if city is not None:
        params["city"] = city

    if min_price is not None:
        params["minPrice"] = min_price

    if max_price is not None:
        params["maxPrice"] = max_price

    if min_bedrooms is not None:
        params["minBedrooms"] = min_bedrooms

    if min_bathrooms is not None:
        params["minBaths"] = min_bathrooms

    if sort_by is not None:
        params["sortBy"] = sort_by

    response = requests.get(
        REPLIERS_URL,
        headers=headers,
        params=params
    )

    response.raise_for_status()

    data = response.json()

    listings = data.get("listings", [])

    normalized_listings = []

    for listing in listings:
        normalized_listing = normalize_listing(listing)
        normalized_listings.append(normalized_listing)

    return {
    "page": data.get("page"),
    "totalPages": data.get("numPages"),
    "pageSize": data.get("pageSize"),
    "totalListings": data.get("count"),
    "listings": normalized_listings
    
}
