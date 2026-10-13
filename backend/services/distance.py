import math


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculates the straight-line distance between two locations
    on Earth using their latitude and longitude.

    The Haversine formula is used because the Earth is curved.

    lat1, lon1 = coordinates of the first location (the home)
    lat2, lon2 = coordinates of the second location (nearby place)

    The distance is returned in miles.
    """

    # Approximate radius of the Earth in miles.
    # Using miles means our final distance will also be in miles.
    earth_radius_miles = 3958.8

    # Latitude and longitude are normally given in degrees,
    # but Python's trigonometry functions work with radians.
    # Convert all four coordinates from degrees to radians.
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Find the difference between the two locations'
    # latitude and longitude.
    difference_lat = lat2 - lat1
    difference_lon = lon2 - lon1

    # This is the first part of the Haversine formula.
    # It accounts for the Earth's curved surface when comparing
    # the coordinates of the two locations.
    a = (
        math.sin(difference_lat / 2) ** 2
        + math.cos(lat1)
        * math.cos(lat2)
        * math.sin(difference_lon / 2) ** 2
    )

    # Calculate the angle between the two locations
    # along the surface of the Earth.
    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    # Convert that angle into a distance by multiplying
    # it by the Earth's radius.
    distance = earth_radius_miles * c

    # Return the distance rounded to two decimal places.
    # Example: 1.80347 miles becomes 1.80 miles.
    return round(distance, 2)