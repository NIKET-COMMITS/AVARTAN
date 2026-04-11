import math
from typing import List, Dict, Any

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates distance between two GPS points in kilometers."""
    R = 6371.0 # Earth radius in kilometers
    
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c

def rank_facilities(facilities_list: List[Dict[str, Any]], max_distance: float = 25) -> List[Dict[str, Any]]:
    """Ranks facilities based on Rating (40%) and Distance (30%)."""
    scored = []
    for item in facilities_list:
        facility = item["facility"]
        distance = item["distance_km"]
        
        if distance > max_distance:
            continue
            
        rating_score = (facility.rating / 5) * 40 if facility.rating > 0 else 0
        distance_score = max(0, (1 - distance / max_distance) * 30)
        
        total_score = rating_score + distance_score + (10 if facility.is_verified else 0)
        
        scored.append({
            "facility": facility,
            "distance_km": round(distance, 2),
            "score": round(total_score, 2)
        })
        
    return sorted(scored, key=lambda x: x["score"], reverse=True)