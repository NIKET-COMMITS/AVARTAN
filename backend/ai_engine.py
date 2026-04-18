"""
Zero-Budget Hybrid AI Engine
Combines Rule-Based Logic with Scikit-Learn TF-IDF (Lightweight RAG)
Optimized for low-RAM Free-Tier Servers. No paid APIs required.
"""

import math
from typing import Dict, List, Any, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# --- 1. LOCAL KNOWLEDGE BASE (For Lightweight RAG) ---
# In a larger app, this could be loaded from a JSON file.
WASTE_KNOWLEDGE_BASE = [
    {
        "text": "Plastic water bottles, soda bottles, and clear containers made of PET or PETE. Highly recyclable. Clean before recycling.",
        "material": "plastic",
        "condition": "good",
        "base_value_per_kg": 15.0,
        "co2_saved_per_kg": 1.5,
        "advice": "Rinse out any liquid. Keep the cap on as it is also recyclable in most modern facilities."
    },
    {
        "text": "Cardboard boxes, shipping boxes, paper bags, corrugated cardboard. Keep dry and flatten before recycling.",
        "material": "paper",
        "condition": "good",
        "base_value_per_kg": 8.0,
        "co2_saved_per_kg": 3.0,
        "advice": "Flatten the boxes to save space. Remove tape if possible. Must be kept dry; wet cardboard is often rejected."
    },
    {
        "text": "Aluminum cans, soda cans, tin cans, metal containers. Very high value and infinitely recyclable.",
        "material": "metal",
        "condition": "good",
        "base_value_per_kg": 120.0,
        "co2_saved_per_kg": 9.0,
        "advice": "Empty completely. Crushing them saves space but check if your local facility prefers them uncrushed for sorting."
    },
    {
        "text": "Old smartphones, laptops, broken electronics, circuit boards, e-waste, chargers, wires.",
        "material": "e-waste",
        "condition": "broken",
        "base_value_per_kg": 200.0,  # Varies heavily
        "co2_saved_per_kg": 5.0,
        "advice": "Do not throw in normal trash! Contains heavy metals. Ensure data is wiped before handing over smartphones or laptops."
    },
    {
        "text": "Glass bottles, jars, clear, green, or brown glass. Fragile but infinitely recyclable.",
        "material": "glass",
        "condition": "good",
        "base_value_per_kg": 2.0,
        "co2_saved_per_kg": 0.3,
        "advice": "Rinse out food residue. Separate by color if required by your local center. Broken glass must be handled carefully."
    }
]

# --- 2. FAST RULE-BASED DICTIONARY ---
# Covers 80% of common queries instantly without ML overhead.
COMMON_ITEMS = {
    "bottle": "plastic",
    "box": "paper",
    "can": "metal",
    "phone": "e-waste",
    "laptop": "e-waste",
    "jar": "glass",
    "newspaper": "paper"
}


class WasteAIEngine:
    def __init__(self):
        # Initialize Lightweight RAG Vectorizer
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
        # Prepare the corpus (documents) for the vector space
        self.corpus = [item["text"] for item in WASTE_KNOWLEDGE_BASE]
        
        # Fit and transform the knowledge base into a TF-IDF matrix
        # This uses practically zero RAM and takes milliseconds
        self.knowledge_matrix = self.vectorizer.fit_transform(self.corpus)

    def classify_waste(self, description: str) -> Dict[str, Any]:
        """
        Step 1: Check Rule-Based logic for fast matching.
        Step 2: Fallback to Lightweight RAG (TF-IDF Cosine Similarity).
        """
        desc_lower = description.lower()
        
        # 1. Rule-Based Fast Pass
        for key, material in COMMON_ITEMS.items():
            if key in desc_lower:
                # Find the corresponding knowledge base entry to grab stats
                for kb_item in WASTE_KNOWLEDGE_BASE:
                    if kb_item["material"] == material:
                        return {
                            "method": "rule_based",
                            "material": material,
                            "confidence": 0.95,
                            "estimated_value_per_kg": kb_item["base_value_per_kg"],
                            "co2_saved_per_kg": kb_item["co2_saved_per_kg"],
                            "advice": kb_item["advice"]
                        }

        # 2. Lightweight RAG Retrieval Pass
        # Vectorize the user's query
        query_vector = self.vectorizer.transform([description])
        
        # Calculate cosine similarity between query and all knowledge base documents
        similarities = cosine_similarity(query_vector, self.knowledge_matrix)[0]
        
        # Get the index of the highest scoring document
        best_match_idx = similarities.argmax()
        best_score = similarities[best_match_idx]
        
        # If the score is too low, we don't have enough context
        if best_score < 0.15:
            return {
                "method": "rag_fallback",
                "material": "unknown",
                "confidence": float(best_score),
                "estimated_value_per_kg": 0.0,
                "co2_saved_per_kg": 0.0,
                "advice": "Unable to confidently classify this waste. Please check with a local facility."
            }
            
        match = WASTE_KNOWLEDGE_BASE[best_match_idx]
        return {
            "method": "rag_retrieval",
            "material": match["material"],
            "confidence": float(best_score),
            "estimated_value_per_kg": match["base_value_per_kg"],
            "co2_saved_per_kg": match["co2_saved_per_kg"],
            "advice": match["advice"]
        }

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Haversine formula to calculate distance between two coordinates in KM"""
        R = 6371.0  # Earth radius in kilometers

        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad

        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c
        return distance

    def score_and_rank_facilities(self, user_lat: float, user_lon: float, material: str, facilities: List[Any]) -> List[Dict]:
        """
        Smart Recommendations Algorithm.
        Scores facilities based on: Distance (40%), Rating (30%), Material Match (30%)
        """
        ranked_list = []
        
        for fac in facilities:
            # 1. Calculate Distance
            dist_km = self.calculate_distance(user_lat, user_lon, fac.latitude, fac.longitude)
            
            # Distance Score (Inverse: closer is better. Max score = 40)
            # Assuming 50km is the max reasonable distance
            dist_score = max(0, 40 - (dist_km * 0.8)) 
            
            # 2. Rating Score (Max score = 30)
            # A 5-star rating gives 30 points
            rating_score = (fac.rating / 5.0) * 30 if fac.rating else 15 # Default to average if no rating
            
            # 3. Material Match Score (Max score = 30)
            # In a real scenario, fac.materials_accepted would be a JSON list
            material_score = 0
            if fac.materials_accepted and material in fac.materials_accepted:
                material_score = 30
            elif not fac.materials_accepted:
                # If facility doesn't specify, give partial credit
                material_score = 10
                
            total_score = dist_score + rating_score + material_score
            
            ranked_list.append({
                "facility_id": fac.id,
                "name": fac.name,
                "distance_km": round(dist_km, 2),
                "rating": fac.rating,
                "score": round(total_score, 2),
                "accepts_material": material_score > 10
            })
            
        # Sort descending by score
        ranked_list.sort(key=lambda x: x["score"], reverse=True)
        return ranked_list

# Singleton instance to be imported and used across the app
ai_engine = WasteAIEngine()