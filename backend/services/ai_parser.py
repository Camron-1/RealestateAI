
import os
import json
from typing import Literal

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel


# -----------------------------------
# Load environment variables
# -----------------------------------

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# -----------------------------------
# Define AI search preferences
# -----------------------------------

class HomeSearch(BaseModel):
    city: str | None = None
    state: str | None = None
    max_price: int | None = None
    property_type: str | None = None

    min_bedrooms: int | None = None
    min_bathrooms: int | None = None

    bedroom_mode: Literal[
        "exact", "minimum", "maximum"
    ] | None = None

    bathroom_mode: Literal[
        "exact", "minimum", "maximum"
    ] | None = None

    wants_hospital: bool = False
    wants_school: bool = False
    wants_park: bool = False
    wants_dog_park: bool = False
    wants_playground: bool = False


# -----------------------------------
# Shared Gemini request
# -----------------------------------

def generate_preferences(prompt):
    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": HomeSearch,
        },
    )

    if response.parsed is None:
        raise ValueError(
            "Gemini could not parse the home search."
        )

    preferences = response.parsed.model_dump()

# Generic house/home searches should not restrict property type.
    if preferences.get("property_type") in ("house", "home"):
      preferences["property_type"] = None

    return preferences


# -----------------------------------
# Initial home search
# -----------------------------------

def parse_home_search(user_query):
    prompt = f"""
    Convert the user's home search into structured data.

    USER SEARCH:
    {user_query}

    RULES:

    LOCATION:
    - Extract city and state when provided.
    - Convert state names to two-letter abbreviations.
    - Example: North Carolina becomes NC.

    PRICE:
    - Convert prices to integers.
    - Example: 300k becomes 300000.
    - Only set max_price for a maximum budget.

    BEDROOMS:
    - "2 bedrooms" means exactly 2.
    - "At least 2 bedrooms" means 2 or more.
    - "2+ bedrooms" means 2 or more.
    - "Up to 3 bedrooms" means 3 or fewer.
    - Store the number in min_bedrooms.
    - Set bedroom_mode to exact, minimum, or maximum.

    BATHROOMS:
    - Apply the same rules as bedrooms.
    - Store the number in min_bathrooms.
    - Set bathroom_mode appropriately.

    PROPERTY TYPE:
    - Only set property_type if explicitly specified.
    - Generic words such as house or home should
      not restrict property_type.

    AMENITIES:
    - Set wants_hospital to true only if requested.
    - Set wants_school to true only if requested.
    - Set wants_park to true only if requested.
    - Set wants_dog_park to true only if requested.
    - Set wants_playground to true only if requested.

    IMPORTANT:
    - Do not invent requirements.
    - Use null for unspecified optional fields.
    - Use false for amenities not requested.
    """

    return generate_preferences(prompt)


# -----------------------------------
# Follow-up conversational search
# -----------------------------------

def parse_followup_search(
    user_message,
    previous_preferences=None
):
    previous_preferences = previous_preferences or {}

    prompt = f"""
    You are the RealestateAI home-search assistant.

    The user has already searched for homes.
    Update their preferences based on the new message.

    PREVIOUS PREFERENCES:
    {json.dumps(previous_preferences)}

    NEW MESSAGE:
    {user_message}

    RULES:

    - Preserve all previous preferences unless changed.
    - Return the complete updated preferences.
    - Do not invent requirements.

    BEDROOMS:
    - "Make it 3 bedrooms" means exactly 3.
    - "At least 3 bedrooms" means 3 or more.
    - "3+ bedrooms" means 3 or more.
    - "Up to 3 bedrooms" means 3 or fewer.
    - Store the count in min_bedrooms.
    - Update bedroom_mode appropriately.

    BATHROOMS:
    - Apply the same rules to bathrooms.
    - Store the count in min_bathrooms.
    - Update bathroom_mode appropriately.

    LOCATION:
    - Preserve the previous city and state
      unless the user changes them.
    - Convert state names to abbreviations.

    PRICE:
    - Preserve the previous budget unless changed.
    - Convert prices such as 400k to 400000.

    AMENITIES:
    - Preserve previously requested amenities.
    - Set an amenity to false if the user removes it.
    - Set an amenity to true if newly requested.

    REMOVING REQUIREMENTS:
    - If bedrooms are removed, set min_bedrooms
      and bedroom_mode to null.
    - If bathrooms are removed, set min_bathrooms
      and bathroom_mode to null.
    - Clear other removed requirements as appropriate.

    Return the full updated search preferences.
    """

    return generate_preferences(prompt)
