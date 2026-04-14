# backend/data/facilities_data.py

# Highly realistic simulated data for Gandhinagar, Gujarat (Zero Budget Approach)
# Renamed to FACILITIES_DATA to fix the ImportError in database.py
FACILITIES_DATA = [
    {
        "id": 1,
        "name": "Gandhinagar E-Waste & Tech Recycling Hub",
        "lat": 23.2200, 
        "lon": 72.6500,
        "accepted_materials": ["e-waste", "electronics", "metal", "batteries"],
        "phone": "+91 98765 43210",
        "website": "www.gnr-ewaste.in",
        "google_rating": 4.8,
        "total_reviews": 124,
        "address": "Sector 16, Electronic Estate, Gandhinagar",
        "hours": {"open": 9, "close": 18} # 9 AM to 6 PM (24hr format)
    },
    {
        "id": 2,
        "name": "Green Planet Plastic Recyclers",
        "lat": 23.1900, 
        "lon": 72.6100,
        "accepted_materials": ["plastic", "glass", "pet", "bottles"],
        "phone": "+91 99887 76655",
        "website": "www.greenplanet-guj.com",
        "google_rating": 4.5,
        "total_reviews": 89,
        "address": "GIDC Sector 25, Gandhinagar",
        "hours": {"open": 8, "close": 20} # 8 AM to 8 PM
    },
    {
        "id": 3,
        "name": "Sector 21 Organic Composting Plant",
        "lat": 23.2300, 
        "lon": 72.6400,
        "accepted_materials": ["organic", "food waste", "leaves", "wood"],
        "phone": "+91 91234 56789",
        "website": "www.gnr-compost.gov.in",
        "google_rating": 4.2,
        "total_reviews": 45,
        "address": "Sector 21 Municipal Ground, Gandhinagar",
        "hours": {"open": 6, "close": 14} # 6 AM to 2 PM
    },
    {
        "id": 4,
        "name": "Gujarat Paper & Cardboard Mills",
        "lat": 23.2000, 
        "lon": 72.6600,
        "accepted_materials": ["paper", "cardboard", "cartons", "mixed"],
        "phone": "+91 90000 11111",
        "website": "None",
        "google_rating": 3.9,
        "total_reviews": 210,
        "address": "Sargasan Cross Road, Gandhinagar",
        "hours": {"open": 10, "close": 19} # 10 AM to 7 PM
    },
    {
        "id": 5,
        "name": "Universal Scrap Traders (Bulk & Mixed)",
        "lat": 23.2500, 
        "lon": 72.6200,
        "accepted_materials": ["metal", "other", "mixed", "furniture", "appliances"],
        "phone": "+91 98888 22222",
        "website": "None",
        "google_rating": 4.6,
        "total_reviews": 312,
        "address": "Pethapur, Gandhinagar",
        "hours": {"open": 8, "close": 22} # 8 AM to 10 PM
    }
]
from fastapi import APIRouter, Query
from backend.services.location_service import location_service

router = APIRouter(prefix="/facilities", tags=["Facilities"])

@router.get("/nearby")
async def get_nearby_facilities(
    lat: float = Query(23.2156, description="User Latitude (Default: Gandhinagar Center)"),
    lon: float = Query(72.6369, description="User Longitude (Default: Gandhinagar Center)"),
    material: str = Query("plastic", description="Material to recycle")
):
    """
    Finds the top 3 best facilities within 25km based on real GPS distance and operating hours.
    """
    facilities = location_service.find_best_facilities(
        user_lat=lat, 
        user_lon=lon, 
        material=material, 
        max_radius_km=25.0
    )
    
    return {
        "success": True,
        "data": facilities,
        "message": f"Found {len(facilities)} facilities near you accepting {material}."
    }