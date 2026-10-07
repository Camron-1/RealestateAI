from fastapi import FastAPI

from services.repliers import get_listings
from services.overpass import get_nearby_places
from services.distance import calculate_distance

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
    min_price: int | None = None,
    max_price: int | None = None,
    min_bedrooms: int | None = None,
    min_bathrooms: int | None = None,
     page: int = 1,
    results_per_page: int = 10,
    sort_by: str | None = None
):
    return get_listings(
        city=city,
        min_price=min_price,
        max_price=max_price,
        min_bedrooms=min_bedrooms,
        min_bathrooms=min_bathrooms,
        page=page,
        results_per_page=results_per_page,
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
        "distance miles": calculate_distance(lat1, lon1, lat2, lon2)
    }