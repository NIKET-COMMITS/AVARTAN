"""
Cost Analysis Service
Calculates economic and environmental benefits of routes
"""

from typing import Dict
import logging

logger = logging.getLogger("avartan")

class CostAnalyzer:
    """Analyzes costs and benefits of different routes"""
    
    RUPEES_PER_CO2_KG = 500
    TRANSPORTATION_COST_PER_KM = 5
    PROCESSING_TIME_PER_ITEM = 15
    
    def analyze_route(self, estimated_value: float, co2_saved_kg: float,
                     distance_km: float, facility_rating: float = 4.0,
                     user_eco_preference: float = 0.5) -> Dict:
        """Comprehensive cost-benefit analysis"""
        
        economic_benefit = estimated_value
        environmental_value = co2_saved_kg * self.RUPEES_PER_CO2_KG
        travel_cost = distance_km * self.TRANSPORTATION_COST_PER_KM
        
        net_benefit = environmental_value + economic_benefit - travel_cost
        
        value_per_km = economic_benefit / distance_km if distance_km > 0 else 0
        co2_per_km = co2_saved_kg / distance_km if distance_km > 0 else 0
        break_even_km = travel_cost / (environmental_value + economic_benefit) if (environmental_value + economic_benefit) > 0 else 0
        
        incentive_eligible = (co2_saved_kg > 50 and economic_benefit > 1000)
        estimated_incentive = 500 if incentive_eligible else 0
        
        recommendation = self._generate_recommendation(net_benefit, co2_saved_kg, user_eco_preference)
        
        return {
            'economic_benefit': round(economic_benefit, 0),
            'environmental_benefit': round(environmental_value, 0),
            'travel_cost': round(travel_cost, 2),
            'net_benefit': round(net_benefit, 0),
            'value_per_km': round(value_per_km, 2),
            'co2_per_km': round(co2_per_km, 2),
            'break_even_km': round(break_even_km, 4),
            'incentive_eligible': incentive_eligible,
            'estimated_incentive': estimated_incentive,
            'total_with_incentive': round(net_benefit + estimated_incentive, 0),
            'facility_rating_bonus': facility_rating * 100,
            'recommendation': recommendation,
            'recommended': net_benefit > 100,
        }
    
    @staticmethod
    def _generate_recommendation(net_benefit: float, co2_saved: float, eco_pref: float) -> str:
        """Generate recommendation message"""
        if net_benefit < 0: return "Not recommended - Cost exceeds benefit"
        
        if eco_pref > 0.7:
            return "⭐ Highly recommended - Excellent environmental impact!" if co2_saved > 100 else "✓ Recommended - Good environmental choice"
        else:
            return "⭐ Highly recommended - Strong economic benefit!" if net_benefit > 2000 else "✓ Recommended - Reasonable economic return"

cost_analyzer = CostAnalyzer()