from fastapi import FastAPI
from services.property_questions import (
    classify_message,
    answer_property_question,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.ai_parser import parse_followup_search

from services.home_search import search_homes
from services.ai_parser import parse_home_search
from services.repliers import get_listings
from services.distance import calculate_distance
from services.overpass import get_nearby_places


# -----------------------------------
# Create FastAPI application
# -----------------------------------

app = FastAPI(
    title="AI Home Finder API",
    version="1.0.0"
)
class AIChatRequest(BaseModel):
    message: str
    previous_preferences: dict | None = None
    previous_results: list | None = None
    manual_filters: dict | None = None


# -----------------------------------
# Allow React frontend connections
# -----------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------------
# Root endpoint
# -----------------------------------

@app.get("/")
def root():
    return {
        "message": "AI Home Finder API is running"
    }


# -----------------------------------
# Get home listings
# -----------------------------------

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


# -----------------------------------
# Find nearby amenities
# -----------------------------------

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


# -----------------------------------
# Calculate distance
# -----------------------------------

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


# -----------------------------------
# Search homes with nearby amenities
# -----------------------------------

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


# -----------------------------------
# AI-powered natural language search
# -----------------------------------

@app.get("/ai-search")
def ai_search(query: str):

    # Step 1: Gemini parses the user's request
    preferences = parse_home_search(query)

    print("AI SEARCH QUERY:", query)
    print("AI SEARCH PREFERENCES:", preferences)

    # Step 2: Find and rank matching homes
    listings = search_homes(
        city=preferences.get("city"),
        state=preferences.get("state"),
        max_price=preferences.get("max_price"),
        property_type=preferences.get("property_type"),

        min_bedrooms=preferences.get("min_bedrooms"),
        min_bathrooms=preferences.get("min_bathrooms"),

        bedroom_mode=(
            preferences.get("bedroom_mode") or "exact"
        ),
        bathroom_mode=(
            preferences.get("bathroom_mode") or "exact"
        ),

        wants_hospital=preferences.get(
            "wants_hospital", False
        ),
        wants_school=preferences.get(
            "wants_school", False
        ),
        wants_park=preferences.get(
            "wants_park", False
        ),
        wants_dog_park=preferences.get(
            "wants_dog_park", False
        ),
        wants_playground=preferences.get(
            "wants_playground", False
        )
    )

    print("HOMES RETURNED:", len(listings))

    # Step 3: Return results to React
    return {
        "search_preferences": preferences,
        "results": listings
    }


@app.post("/ai-chat")

@app.post("/ai-chat")
def ai_chat(request: AIChatRequest):

    previous_results = request.previous_results or []

    # Manual filter requests must always trigger a search.
    # Property questions should reuse existing listings.
    if request.manual_filters is not None:
        intent = "search"
    else:
        intent = classify_message(
            message=request.message,
            has_results=len(previous_results) > 0
        )

    print("AI CHAT MESSAGE:", request.message)
    print("DETECTED INTENT:", intent)

    # -----------------------------------
    # Answer questions about existing homes
    # -----------------------------------
    if intent == "property_question":

        reply = answer_property_question(
            message=request.message,
            listings=previous_results,
            preferences=request.previous_preferences
        )

        return {
            "reply": reply,
            "intent": "property_question",
            "search_preferences": request.previous_preferences,
            "results": previous_results
        }

    # -----------------------------------
    # Update search preferences with Gemini
    # -----------------------------------

    # For a filter-only request, keep existing preferences
    # instead of asking Gemini to interpret placeholder text.
    filter_only_message = request.message in (
        "Update my search using the selected filters",
        "Apply my selected home search filters"
    )

    if filter_only_message and request.previous_preferences:
        preferences = dict(request.previous_preferences)
    else:
        preferences = parse_followup_search(
            user_message=request.message,
            previous_preferences=request.previous_preferences
        )

    # -----------------------------------
    # Apply manually selected filters
    # -----------------------------------
    if request.manual_filters is not None:

        filters = request.manual_filters

        # Bedrooms: minimum count
        if "min_bedrooms" in filters:
            bedrooms = filters["min_bedrooms"]

            preferences["min_bedrooms"] = bedrooms
            preferences["bedroom_mode"] = (
                "minimum" if bedrooms is not None else None
            )

        # Bathrooms: minimum count
        if "min_bathrooms" in filters:
            bathrooms = filters["min_bathrooms"]

            preferences["min_bathrooms"] = bathrooms
            preferences["bathroom_mode"] = (
                "minimum" if bathrooms is not None else None
            )

        # Maximum price
        if "max_price" in filters:
            preferences["max_price"] = filters["max_price"]

        # Nearby amenities
        if "amenities" in filters:
            selected_amenities = filters["amenities"] or []

            for amenity in [
                "hospital",
                "school",
                "park",
                "dog_park",
                "playground"
            ]:
                preferences[f"wants_{amenity}"] = (
                    amenity in selected_amenities
                )

    print("UPDATED PREFERENCES:", preferences)

    # -----------------------------------
    # Check for city
    # -----------------------------------
    if not preferences.get("city"):
        return {
            "reply": "What city would you like to search for homes in?",
            "intent": "search",
            "search_preferences": preferences,
            "results": []
        }

    # -----------------------------------
    # Search Repliers
    # -----------------------------------
    listings = search_homes(
        city=preferences.get("city"),
        state=preferences.get("state"),
        max_price=preferences.get("max_price"),
        property_type=preferences.get("property_type"),
        min_bedrooms=preferences.get("min_bedrooms"),
        min_bathrooms=preferences.get("min_bathrooms"),
        bedroom_mode=preferences.get("bedroom_mode") or "exact",
        bathroom_mode=preferences.get("bathroom_mode") or "exact",
        wants_hospital=preferences.get("wants_hospital", False),
        wants_school=preferences.get("wants_school", False),
        wants_park=preferences.get("wants_park", False),
        wants_dog_park=preferences.get("wants_dog_park", False),
        wants_playground=preferences.get("wants_playground", False)
    )

    count = len(listings)

    # -----------------------------------
    # Generate assistant response
    # -----------------------------------
    if count == 0:
        reply = (
            "I couldn't find homes matching those requirements. "
            "Would you like to adjust your search?"
        )
    else:
        reply = (
            f"I found {count} homes matching your preferences. "
            "You can refine your search or ask me questions "
            "about these properties."
        )

    return {
        "reply": reply,
        "intent": "search",
        "search_preferences": preferences,
        "results": listings
    }
