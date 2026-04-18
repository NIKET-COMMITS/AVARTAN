import os

code = """class GamificationService:
    def calculate_impact(self, material: str, weight_kg: float) -> tuple[int, float]:
        mat = material.lower()
        if "plastic" in mat:
            co2 = weight_kg * 1.5
            points = int(weight_kg * 50)
        elif "metal" in mat or "aluminum" in mat:
            co2 = weight_kg * 2.0
            points = int(weight_kg * 80)
        elif "paper" in mat or "cardboard" in mat:
            co2 = weight_kg * 0.5
            points = int(weight_kg * 20)
        elif "glass" in mat:
            co2 = weight_kg * 0.3
            points = int(weight_kg * 15)
        else:
            co2 = weight_kg * 1.0
            points = int(weight_kg * 30)
            
        return points, round(co2, 2)

# Export the instance so waste.py can import it
gamification_service = GamificationService()
"""

# Ensure the directory exists
os.makedirs(os.path.join("backend", "services"), exist_ok=True)

# Force overwrite the file on the disk
file_path = os.path.join("backend", "services", "gamification_service.py")
with open(file_path, "w", encoding="utf-8") as f:
    f.write(code)

print("✅ SUCCESS! gamification_service.py has been physically saved to the disk.")