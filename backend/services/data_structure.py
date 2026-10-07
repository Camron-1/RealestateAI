def normalize_listing(listing):
    address = listing.get("address", {})
    details = listing.get("details", {})
    map_data = listing.get("map", {})

    return {
        "id": listing.get("mlsNumber"),
        "price": listing.get("listPrice"),
        "status": listing.get("status"),

        "address": {
            "streetNumber": address.get("streetNumber"),
            "streetDirection": address.get("streetDirectionPrefix"),
            "streetName": address.get("streetName"),
            "streetSuffix": address.get("streetSuffix"),
            "unit": address.get("unitNumber"),
            "city": address.get("city"),
            "state": address.get("state"),
            "zip": address.get("zip")
        },

        "bedrooms": details.get("numBedrooms"),
        "bathrooms": details.get("numBathrooms"),
        "sqft": details.get("sqft"),
        "yearBuilt": details.get("yearBuilt"),

        "propertyType": details.get("propertyType"),
        "style": details.get("style"),

        "garageSpaces": details.get("numGarageSpaces"),
        "parkingSpaces": details.get("numParkingSpaces"),

        "latitude": map_data.get("latitude"),
        "longitude": map_data.get("longitude"),

        "description": details.get("description"),

        "images": listing.get("images", [])
    }
def normalize_place(place):
    tags = place.get("tags", {})
    center = place.get("center", {})

    return {
        "id": place.get("id"),
        "name": tags.get("name"),
        "type": tags.get("amenity") or tags.get("leisure"),
        "latitude": place.get("lat") or center.get("lat"),
        "longitude": place.get("lon") or center.get("lon")
    }