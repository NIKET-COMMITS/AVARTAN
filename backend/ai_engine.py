"""
Zero-Budget Hybrid AI Engine
Combines Rule-Based Logic with Scikit-Learn TF-IDF (Lightweight RAG)
Now features the Universal Diagnostic & Appraisal System for all item types.
"""

import math
from typing import Dict, List, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- LOCAL KNOWLEDGE BASE (For Lightweight RAG) ---
WASTE_KNOWLEDGE_BASE = [
    {
        "text": "Plastic water bottles, soda bottles, and clear containers made of PET or PETE. Highly recyclable. Clean before recycling.",
        "material": "plastic",
        "condition": "good",
        "co2_saved_per_kg": 1.5,
        "advice": "Rinse out any liquid. Keep the cap on as it is also recyclable in most modern facilities."
    },
    {
        "text": "Cardboard boxes, shipping boxes, paper bags, corrugated cardboard. Keep dry and flatten before recycling.",
        "material": "paper",
        "condition": "good",
        "co2_saved_per_kg": 3.0,
        "advice": "Flatten the boxes to save space. Remove tape if possible. Must be kept dry; wet cardboard is often rejected."
    },
    {
        "text": "Aluminum cans, soda cans, tin cans, metal containers. Very high value and infinitely recyclable.",
        "material": "metal",
        "condition": "good",
        "co2_saved_per_kg": 9.0,
        "advice": "Empty completely. Crushing them saves space but check if your local facility prefers them uncrushed for sorting."
    },
    {
        "text": "Old smartphones, laptops, broken electronics, circuit boards, e-waste, chargers, wires.",
        "material": "ewaste",
        "condition": "broken",
        "co2_saved_per_kg": 5.0,
        "advice": "Do not throw in normal trash! Contains heavy metals. Ensure data is wiped before handing over smartphones or laptops."
    },
    {
        "text": "Large home appliances, refrigerators, washing machines, AC units, microwaves.",
        "material": "appliance",
        "condition": "broken",
        "co2_saved_per_kg": 25.0,
        "advice": "Contains refrigerants or heavy motors. Requires specialized corporate recycling."
    }
]

COMMON_ITEMS = {
    "bottle": "plastic",
    "box": "paper",
    "can": "metal",
    "phone": "ewaste",
    "laptop": "ewaste",
    "fridge": "appliance",
    "ac": "appliance",
    "appliance": "appliance"
}

# --- UNIVERSAL AI DIAGNOSTIC & APPRAISAL LOGIC ---
UNIVERSAL_APPRAISAL_LOGIC = {
    "ewaste": {
        "base_value": 50, # Base per kg
        "questions": [
            {"id": "device_type", "label": "What type of device is this?", "options": ["Smartphone", "Laptop/PC", "Tablet", "Cables/Peripherals"]},
            {"id": "brand", "label": "Device Brand / Tier", "options": ["Premium (Apple/Samsung/Dell)", "Standard (HP/Lenovo/Vivo)", "Generic / Unbranded"]},
            {"id": "power_state", "label": "Does it turn on?", "options": ["Yes, fully boots", "Powers on, but screen/hardware broken", "Completely dead"]}
        ]
    },
    "appliance": {
        "base_value": 30, # Heavy scrap metal weight
        "questions": [
            {"id": "appliance_type", "label": "Appliance Type", "options": ["Refrigerator / AC", "Washing Machine / Dryer", "Microwave / Small Appliance"]},
            {"id": "core_part", "label": "Is the core motor/compressor working?", "options": ["Yes, it hums/works", "No, it is dead", "I don't know"]},
            {"id": "rust_level", "label": "Physical Condition", "options": ["Clean / Minor Scratches", "Heavily Rusted / Broken Frame"]}
        ]
    },
    "metal": {
        "base_value": 40, 
        "questions": [
            {"id": "metal_type", "label": "Primary Metal Type", "options": ["Copper (Wires/Pipes)", "Aluminum (Frames/Cans)", "Steel/Iron (Heavy Scrap)", "Mixed/Unknown"]},
            {"id": "purity", "label": "Metal Purity", "options": ["Clean & Stripped", "Painted / Insulated / Attached to plastic"]}
        ]
    },
    "plastic": {
        "base_value": 15,
        "questions": [
            {"id": "plastic_type", "label": "Type of Plastic", "options": ["PET/HDPE (Bottles/Jugs)", "Hard Plastic (Furniture/Toys)", "Mixed/Wrappers"]},
            {"id": "condition", "label": "Is it clean?", "options": ["Clean & Washed", "Dirty / Food Residue"]}
        ]
    },
    "paper": {
        "base_value": 12,
        "questions": [
            {"id": "paper_type", "label": "Paper Type", "options": ["Corrugated Cardboard", "White Office Paper", "Newspaper / Mixed"]},
            {"id": "dryness", "label": "Moisture Level", "options": ["Bone Dry", "Damp / Wet"]}
        ]
    }
}


class WasteAIEngine:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.corpus = [item["text"] for item in WASTE_KNOWLEDGE_BASE]
        self.knowledge_matrix = self.vectorizer.fit_transform(self.corpus)

    def classify_waste(self, description: str) -> Dict[str, Any]:
        """TF-IDF Classification for free-text searches."""
        desc_lower = description.lower()
        
        for key, material in COMMON_ITEMS.items():
            if key in desc_lower:
                for kb_item in WASTE_KNOWLEDGE_BASE:
                    if kb_item["material"] == material:
                        return {
                            "method": "rule_based",
                            "material": material,
                            "confidence": 0.95,
                            "co2_saved_per_kg": kb_item["co2_saved_per_kg"],
                            "advice": kb_item["advice"]
                        }

        query_vector = self.vectorizer.transform([description])
        similarities = cosine_similarity(query_vector, self.knowledge_matrix)[0]
        
        best_match_idx = similarities.argmax()
        best_score = similarities[best_match_idx]
        
        if best_score < 0.15:
            return {
                "method": "rag_fallback",
                "material": "unknown",
                "confidence": float(best_score),
                "co2_saved_per_kg": 0.0,
                "advice": "Unable to confidently classify this waste. Please check with a local facility."
            }
            
        match = WASTE_KNOWLEDGE_BASE[best_match_idx]
        return {
            "method": "rag_retrieval",
            "material": match["material"],
            "confidence": float(best_score),
            "co2_saved_per_kg": match["co2_saved_per_kg"],
            "advice": match["advice"]
        }

    # --- NEW AI DIAGNOSTIC METHODS ---
    def get_appraisal_questions(self, material: str) -> list:
        """Dynamically pulls the correct diagnostic questions based on item category."""
        material = material.lower().replace("-", "")
        # Fallback to plastic/general if unknown
        if material not in UNIVERSAL_APPRAISAL_LOGIC:
            material = "plastic"
        return UNIVERSAL_APPRAISAL_LOGIC[material]["questions"]

    def calculate_exact_value_and_advice(self, material: str, weight: float, answers: dict) -> dict:
        """Acts as an expert appraiser. Returns precise value + structural advice."""
        material = material.lower().replace("-", "")
        if material not in UNIVERSAL_APPRAISAL_LOGIC:
            material = "plastic"

        base = UNIVERSAL_APPRAISAL_LOGIC[material]["base_value"] * weight
        multiplier = 1.0
        bonus = 0.0
        ai_advice = ""
        action_type = "Recycle" # Can be Repair, Sell Parts, or Recycle

        if material == "ewaste":
            device = answers.get("device_type", "")
            brand = answers.get("brand", "")
            power = answers.get("power_state", "")

            if "Smartphone" in device: bonus += 800
            elif "Laptop" in device: bonus += 1500
            
            if "Premium" in brand: multiplier *= 2.5
            elif "Standard" in brand: multiplier *= 1.2

            if "fully boots" in power: 
                multiplier *= 3.0
                action_type = "Sell / Refurbish"
                ai_advice = "Your device is fully functional. Instead of recycling, we strongly recommend selling it second-hand or finding a refurbishing NGO. It retains high market value."
            elif "broken" in power:
                multiplier *= 1.2
                action_type = "Sell for Parts"
                ai_advice = "The device powers on but has broken hardware. High residual value remains in the motherboard, RAM, or battery. Send to an E-waste parts dealer."
            else:
                multiplier *= 0.2
                action_type = "Recycle"
                ai_advice = "Device is completely dead. Value is derived strictly from recovering precious metals (gold/palladium) from the logic board."

        elif material == "appliance":
            a_type = answers.get("appliance_type", "")
            motor = answers.get("core_part", "")
            rust = answers.get("rust_level", "")

            if "Refrigerator" in a_type: base = 35 * weight
            elif "Washing" in a_type: base = 25 * weight

            if "hums/works" in motor:
                multiplier *= 2.0
                action_type = "Repair / Donate"
                ai_advice = "The compressor/motor is still functional! This appliance can easily be repaired by a local technician or donated to an NGO. Do not scrap it yet."
            elif "dead" in motor:
                multiplier *= 0.8
                action_type = "Recycle / Scrap"
                ai_advice = "Core components are dead. Best to send to a heavy metal facility for scrapping. Note: ACs/Fridges require safe refrigerant extraction."

            if "Rusted" in rust: multiplier *= 0.7

        elif material == "metal":
            m_type = answers.get("metal_type", "")
            purity = answers.get("purity", "")
            
            if "Copper" in m_type: base = 600 * weight
            elif "Aluminum" in m_type: base = 120 * weight
            elif "Steel" in m_type: base = 35 * weight

            if "Clean" in purity: 
                multiplier *= 1.2
                ai_advice = "Excellent. Clean, stripped metal fetches premium rates at the scrapyard."
            else: 
                multiplier *= 0.6
                ai_advice = "Mixed or insulated metal requires extra labor to process, lowering your payout. Consider stripping wires if safely possible."

        elif material == "paper":
            p_type = answers.get("paper_type", "")
            dryness = answers.get("dryness", "")
            if "White" in p_type: base = 18 * weight
            if "Bone Dry" in dryness: 
                multiplier *= 1.1
                ai_advice = "Perfectly dry paper is highly desirable for pulping."
            else: 
                multiplier *= 0.2
                ai_advice = "Wet paper loses structural integrity and is highly prone to mold. Most facilities will reject this or pay bare minimum."

        elif material == "plastic":
            p_type = answers.get("plastic_type", "")
            cond = answers.get("condition", "")
            if "PET" in p_type: base = 25 * weight
            if "Clean" in cond: 
                multiplier *= 1.2
                ai_advice = "Cleaned plastic skips the washing phase at the plant, securing you a slightly better rate."
            else: 
                multiplier *= 0.6
                ai_advice = "Contaminated plastic (food residue) often ends up in landfills. Please rinse before recycling!"

        final_price = round((base + bonus) * multiplier, 2)
        
        return {
            "estimated_price": final_price,
            "action_type": action_type,
            "ai_advice": ai_advice
        }

    # --- ROUTING & SCORING ---
    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine formula to calculate distance between two coordinates in KM"""
        R = 6371.0
        lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
        lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)

        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad

        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def score_and_rank_facilities(self, user_lat: float, user_lon: float, material: str, facilities: List[Any], exact_price: float = 0.0) -> List[Dict]:
        """
        Ranks strictly by Distance + Quality Rating.
        Now injects the calculated AI price into the final output.
        """
        ranked_list = []
        
        for fac in facilities:
            dist_km = self.calculate_distance(user_lat, user_lon, fac.latitude, fac.longitude)
            
            dist_score = max(0, 60 - (dist_km * 1.5)) 
            rating_score = (fac.rating / 5.0) * 40 if fac.rating else 20
            total_score = dist_score + rating_score
            
            # Slightly adjust price based on facility premium rating
            facility_payout = round(exact_price * (1 + ((fac.rating or 4)/100)), 2) if exact_price > 0 else 0.0

            ranked_list.append({
                "facility_id": fac.id,
                "name": fac.name,
                "latitude": fac.latitude,
                "longitude": fac.longitude,
                "distance_km": round(dist_km, 2),
                "rating": fac.rating,
                "score": round(total_score, 1),
                "estimated_price": facility_payout
            })
            
        ranked_list.sort(key=lambda x: x["score"], reverse=True)
        return ranked_list

# Singleton instance
ai_engine = WasteAIEngine()