
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("REPLIERS_API_KEY")

if not API_KEY:
    raise ValueError("REPLIERS_API_KEY not found in .env")

url = "https://api.repliers.io/listings"

headers = {
    "REPLIERS-API-KEY": API_KEY
}

params = {
    "status": "A",
    "aggregates": "address.city",
    "listings": "false"
}

response = requests.get(
    url,
    headers=headers,
    params=params,
    timeout=30
)

print("HTTP STATUS:", response.status_code)
response.raise_for_status()

data = response.json()

print("\nAVAILABLE CITY DATA:\n")
print(data.get("aggregates", data))
