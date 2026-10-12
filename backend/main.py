from fastapi import FastAPI
from services.home_search import search_homes
from services.ai_parser import parse_home_search
from services.repliers import get_listings
from services.distance import calculate_distance
from services.overpass import get_nearby_places, get_closest_places
from services.ranking import calculate_home_score

app = FastAPI(
    title="AI Home Finder API",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "AI Home Finder API is running"
    }


@app.get("/homes")
def homes(
    city: str | None = None,
    state: str | None = None,
    min_price: int | None = None,
    max_price: int | None = None,
    min_bedrooms: int | None = None,
    min_bathrooms: int | None = None,
    property_type: str | None = None,
    page: int = 1,
    results_per_page: int = 10,
    sort_by: str | None = None
):
    return get_listings(
        city=city,
        state=state,
        min_price=min_price,
        max_price=max_price,
        min_bedrooms=min_bedrooms,
        min_bathrooms=min_bathrooms,
        page=page,
        results_per_page=results_per_page,
        property_type=property_type,
        sort_by=sort_by
    )


@app.get("/nearby")
def nearby(
    latitude: float,
    longitude: float,
    radius: int = 5000
):
    return get_nearby_places(
        latitude=latitude,
        longitude=longitude,
        radius=radius
    )


@app.get("/distance")
def distance(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float
):
    return {
        "distance_miles": calculate_distance(
            lat1,
            lon1,
            lat2,
            lon2
        )
    }


@app.get("/home-with-nearby")
def home_with_nearby(
    city: str,
    state: str | None = None,
    max_price: int | None = None,
    property_type: str | None = None,
    min_bedrooms: int | None = None,
    min_bathrooms: int | None = None,
    wants_hospital: bool = False,
    wants_school: bool = False,
    wants_park: bool = False,
    wants_dog_park: bool = False,
    wants_playground: bool = False
):

    listings = search_homes(
        city=city,
        state=state,
        max_price=max_price,
        property_type=property_type,
        min_bedrooms=min_bedrooms,
        min_bathrooms=min_bathrooms,
        wants_hospital=wants_hospital,
        wants_school=wants_school,
        wants_park=wants_park,
        wants_dog_park=wants_dog_park,
        wants_playground=wants_playground
    )

    if not listings:
        return {
            "message": "No homes found"
        }

    return listings


@app.get("/ai-search")
def ai_search(query: str):

    # -----------------------------------
    # Step 1: Gemini understands the user
    # -----------------------------------

    preferences = parse_home_search(query)

    # -----------------------------------
    # Step 2: Search using those preferences
    # -----------------------------------

    listings = search_homes(
        city=preferences.get("city"),
        state=preferences.get("state"),
        max_price=preferences.get("max_price"),
        property_type=preferences.get("property_type"),
        min_bedrooms=preferences.get("min_bedrooms"),
        min_bathrooms=preferences.get("min_bathrooms"),
        wants_hospital=preferences.get(
            "wants_hospital",
            False
        ),
        wants_school=preferences.get(
            "wants_school",
            False
        ),
        wants_park=preferences.get(
            "wants_park",
            False
        ),
        wants_dog_park=preferences.get(
            "wants_dog_park",
            False
        ),
        wants_playground=preferences.get(
            "wants_playground",
            False
        )
    )

    # -----------------------------------
    # Step 3: Return everything
    # -----------------------------------

    return {
        "search_preferences": preferences,
        "results": listings
    }