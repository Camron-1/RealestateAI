import os

from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel


load_dotenv()


# -----------------------------------
# Create Gemini client
# -----------------------------------

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


# -----------------------------------
# Define the structure we want
# Gemini to return
# -----------------------------------

class HomeSearch(BaseModel):
    city: str | None
    state: str | None
    max_price: int | None
    property_type: str | None
    min_bedrooms: int | None
    min_bathrooms: int | None

    wants_hospital: bool
    wants_school: bool
    wants_park: bool
    wants_dog_park: bool
    wants_playground: bool


# -----------------------------------
# Convert natural language into
# home-search parameters
# -----------------------------------

def parse_home_search(user_query):

    prompt = f"""
    Convert the user's home search into structured data.

    User search:
    {user_query}

    Rules:

    - Convert US state names to two-letter abbreviations.
      Example: Ohio becomes OH.
      North Carolina becomes NC.

    - max_price must be a number.
      Example: 300k becomes 300000.

    - min_bedrooms must be a number if mentioned.

    - min_bathrooms must be a number if mentioned.

    -  Only set property_type if the user explicitly
  specifies a property type.

    - If the user simply says house or home,
  property_type should be null.

    - Set wants_hospital to true only if the user
      asks for a hospital nearby.

    - Set wants_school to true only if the user
      asks for a school nearby.

    - Set wants_park to true only if the user
      asks for a park nearby.

    - Set wants_dog_park to true only if the user
      asks for a dog park nearby.

    - Set wants_playground to true only if the user
      asks for a playground nearby.

    - Do not invent search requirements.

    - If city, state, price, property type, bedrooms,
      or bathrooms are not specified, use null.
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": HomeSearch,
        },
    )

    home_search = response.parsed

    return home_search.model_dump()