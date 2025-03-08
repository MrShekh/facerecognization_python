from geopy.distance import geodesic
from fastapi import HTTPException

# Predefined Worksite Coordinates (Example)
WORKSITE_LOCATION = (22.8171345,72.473485)  # Example: Rai University, Ahmedabad, India
ALLOWED_RADIUS = 0.05  # Radius in KM (50 meters)

def is_within_worksite(employee_location: tuple) -> bool:
    """
    Check if the employee's current location is within the worksite radius.
    """
    distance = geodesic(WORKSITE_LOCATION, employee_location).km
    return distance <= ALLOWED_RADIUS
