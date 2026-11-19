
from services.overpass import get_closest_places

# Charlotte, North Carolina
latitude = 35.2271
longitude = -80.8431

try:
    results = get_closest_places(
        latitude=latitude,
        longitude=longitude,
        radius=5000
    )

    print("\nNEARBY AMENITIES:\n")

    for amenity_type, place in results.items():
        print("Type:", amenity_type)
        print("Name:", place["name"])
        print("Distance:", place["distance_miles"], "miles")
        print("-----------------------------")

    if not results:
        print("No amenities returned within the search radius.")

except Exception as error:
    print("ERROR:", error)
