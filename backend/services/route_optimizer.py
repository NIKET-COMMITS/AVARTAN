"""
Route Optimization Engine
Calculates best routes with weighted scoring
"""

from typing import List, Dict, Tuple
import math
import logging

logger = logging.getLogger("avartan")


class RouteOptimizer:
    """
    Optimizes waste routing with weighted multi-criteria scoring
    """
    
    def __init__(self):
        # Default weights
        self.weights = {
            'value': 0.35,      # 35% - Economic value
            'eco': 0.35,        # 35% - Environmental benefit
            'distance': 0.20,   # 20% - Travel distance
            'quality': 0.10,    # 10% - Facility quality
        }
    
    def set_weights(self, eco_preference: float):
        """Adjust weights based on user eco-preference (0-1)"""
        eco_weight = 0.20 + (eco_preference * 0.30)
        value_weight = 0.50 - (eco_preference * 0.30)
        
        self.weights = {
            'value': value_weight,
            'eco': eco_weight,
            'distance': 0.20,
            'quality': 0.10,
        }
    
    def calculate_route_score(self, estimated_value: float, co2_saved: float,
                            distance_km: float, facility_rating: float,
                            max_value: float = 10000, max_co2: float = 500,
                            max_distance: float = 50) -> float:
        """Calculate route score (0-100)"""
        
        value_score = min(100, (estimated_value / max_value) * 100) * self.weights['value']
        eco_score = min(100, (co2_saved / max_co2) * 100) * self.weights['eco']
        distance_score = max(0, 100 - (distance_km / max_distance * 100)) * self.weights['distance']
        quality_score = (facility_rating / 5.0) * 100 * self.weights['quality']
        
        return round(value_score + eco_score + distance_score + quality_score, 2)
    
    def optimize_route(self, user_location: Tuple[float, float], waste_value: float,
                      co2_potential: float, facilities: List[Dict],
                      eco_preference: float = 0.5) -> List[Dict]:
        """Optimize route selection and return Top 5"""
        
        self.set_weights(eco_preference)
        scored_routes = []
        
        for facility in facilities:
            distance = self._haversine_distance(
                user_location[0], user_location[1],
                facility.get('latitude'), facility.get('longitude')
            )
            
            if distance > 25:
                continue
            
            score = self.calculate_route_score(
                estimated_value=waste_value, co2_saved=co2_potential,
                distance_km=distance, facility_rating=facility.get('rating', 4.0)
            )
            
            scored_routes.append({
                'facility_id': facility.get('id'),
                'facility_name': facility.get('name'),
                'distance_km': round(distance, 2),
                'estimated_value': round(waste_value, 0),
                'estimated_co2_saved': round(co2_potential, 2),
                'facility_rating': facility.get('rating', 4.0),
                'score': score,
            })
        
        scored_routes.sort(key=lambda x: x['score'], reverse=True)
        
        # --- ENHANCED DYNAMIC REASONING ENGINE (XAI) ---
        for idx, route in enumerate(scored_routes[:5]):
            route['rank'] = idx + 1
            
            # Dynamically determine why this facility is a good choice
            if route['distance_km'] < 5:
                route['reason'] = "🚀 Quickest Option: Located very close to you."
            elif route['estimated_co2_saved'] > 8:
                route['reason'] = "🌿 Eco-Friendly: Offers the highest CO2 reduction."
            elif route['facility_rating'] >= 4.5:
                route['reason'] = "⭐ High Quality: Exceptional user ratings and service."
            elif route['estimated_value'] > 1000:
                route['reason'] = "💰 Best Value: Maximum financial return for this item."
            else:
                route['reason'] = "✅ Balanced Choice: Good mix of distance and value."
        
        logger.info(f"Optimized {len(scored_routes)} routes with dynamic reasoning")
        return scored_routes[:5]
    
    @staticmethod
    def _haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in km"""
        R = 6371.0
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

route_optimizer = RouteOptimizer()