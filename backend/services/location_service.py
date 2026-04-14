# backend/services/location_service.py
import math
from datetime import datetime
from backend.data.facilities_data import FACILITIES_DATA

class LocationService:
    @staticmethod
    def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculates Haversine distance between two GPS coordinates in Kilometers.
        """
        R = 6371.0 # Earth radius in kilometers

        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad

        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return round(R * c, 2)

    @staticmethod
    def is_open_now(open_hour: int, close_hour: int) -> bool:
        """Checks if the facility is open based on the current system time."""
        current_hour = datetime.now().hour
        return open_hour <= current_hour < close_hour

    @staticmethod
    def find_best_facilities(user_lat: float, user_lon: float, material: str, max_radius_km: float = 25.0):
        """
        Finds the top 3 closest facilities that accept the material, within a 25km radius.
        """
        material_lower = material.lower()
        matched_facilities = []

        for facility in FACILITIES_DATA:
            # 1. Check if they accept the material (Fuzzy matching)
            accepts_material = any(material_lower in accepted for accepted in facility["accepted_materials"])
            
            # If material is "Other" or "Mixed", fallback to general scrap yards
            if not accepts_material and material_lower in ["other", "mixed"]:
                accepts_material = "mixed" in facility["accepted_materials"]

            if accepts_material:
                # 2. Calculate Distance
                distance = LocationService.calculate_distance(user_lat, user_lon, facility["lat"], facility["lon"])
                
                # 3. Apply 25km radius filter
                if distance <= max_radius_km:
                    
                    # 4. Determine if Open Now
                    is_open = LocationService.is_open_now(facility["hours"]["open"], facility["hours"]["close"])
                    
                    # 5. Generate a 1-click Google Maps Navigation Link
                    maps_url = f"https://www.google.com/maps/dir/?api=1&destination={facility['lat']},{facility['lon']}"

                    facility_data = {
                        "id": facility["id"],
                        "name": facility["name"],
                        "distance_km": distance,
                        "rating": facility["google_rating"],
                        "reviews": facility["total_reviews"],
                        "is_open_now": is_open,
                        "address": facility["address"],
                        "phone": facility["phone"],
                        "navigation_link": maps_url
                    }
                    matched_facilities.append(facility_data)

        # 6. Sort by distance (closest first) and return top 3
        matched_facilities.sort(key=lambda x: x["distance_km"])
        return matched_facilities[:3]

location_service = LocationService()