import os
import requests
from services.data_structure import normalize_listing

from dotenv import load_dotenv


load_dotenv()

REPLIERS_API_KEY = os.getenv("REPLIERS_API_KEY")

REPLIERS_URL = "https://api.repliers.io/listings"


def get_listings():

    headers = {
        "REPLIERS-API-KEY": REPLIERS_API_KEY,
        "Content-Type": "application/json"
    }

    params = {
        "status": "A",
        "type": "sale",
        "resultsPerPage": 10
    }

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

    return normalized_listings