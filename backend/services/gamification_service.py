"""
Gamification Service - Ranks and Rewards
Converts CO2 savings into Levels and Badges
"""

class GamificationService:
    def get_level_info(self, total_co2_saved: float):
        """Returns level name and next level progress"""
        # Define thresholds (kg of CO2 saved)
        levels = [
            (0, "Seedling"),
            (10, "Sprout"),
            (50, "Sapling"),
            (200, "Oak"),
            (500, "Forest Guardian"),
            (1000, "Earth Warrior")
        ]
        
        current_level = "Seedling"
        next_threshold = 10
        
        for i, (threshold, name) in enumerate(levels):
            if total_co2_saved >= threshold:
                current_level = name
                if i + 1 < len(levels):
                    next_threshold = levels[i+1][0]
                else:
                    next_threshold = threshold # Max level reached
        
        progress = min(100, (total_co2_saved / next_threshold) * 100) if next_threshold > 0 else 100
        
        return {
            "level_name": current_level,
            "total_co2_saved": round(total_co2_saved, 2),
            "progress_to_next_level": round(progress, 1),
            "next_milestone": next_threshold
        }

gamification_service = GamificationService()