import io
import json

import google.generativeai as genai
from PIL import Image

from backend.config import settings
from backend.logger import log_error, log_success


class GeminiService:
    def __init__(self):
        if getattr(settings, "GEMINI_API_KEY", None):
            genai.configure(api_key=settings.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={"response_mime_type": "application/json"},
            )
            log_success("AI Service", "Gemini 1.5 Flash initialized in Appraiser Mode")
        else:
            self.model = None
            log_error("AI Service", "No API Key found")

    async def analyze_waste(self, text_input: str = None, image_bytes: bytes = None):
        fallback_item_name = text_input.strip() if text_input else "Scanned Waste Item"
        if not self.model:
            return {"success": True, "data": self.get_fallback(fallback_item_name)}

        # THE "MASTER APPRAISER" PROMPT
        system_prompt = """
        You are AVARTAN's Elite Master Appraiser and Lifecycle Intelligence AI.
        Your job is to deeply analyze the waste item and act as a forensic appraiser.
        
        STRICT RULES:
        1. HUMAN/LIVING SAFETY: If the image contains a human face, person, pet, or landscape, you MUST set "material": "Invalid".
        2. FORENSIC IDENTIFICATION: Identify specific models, brands, and visible wear-and-tear (e.g., 'Samsung TV (Screen Cracked)' or 'PET Plastic Bottle (Crushed)').
        3. THE INTERROGATION: Generate exactly 4 'verification_questions' for the user. These must investigate what the camera CANNOT see. 
           - Q1 (Age): Ask about the time of purchase or age (e.g., "Approximately what year was this purchased?").
           - Q2 (Functionality/Quality): Ask about its working condition (e.g., "Does it still power on?" or "Are there any holes/leaks?").
           - Q3 (Degradation): Ask about its current state vs. when it was new (e.g., "Are all the original parts still attached?").
           - Q4 (Physical Specs): Ask to confirm hidden dimensions/weight (e.g., "Is this heavier than 2 kilograms?").
        
        Respond with ONLY JSON using this exact schema:
        {
          "item_name": "string (Highly specific name)",
          "material": "Metal | Plastic | Paper | Glass | Organic | E-Waste | Mixed | Other | Invalid",
          "estimated_weight": "string (Estimate realistic weight, e.g., '1.2 kg')",
          "size": "Small | Medium | Large",
          "condition": "Mint | Good | Fair | Poor | Broken | Dead",
          "verification_questions": ["string", "string", "string", "string"]
        }
        """

        try:
            if image_bytes:
                image = Image.open(io.BytesIO(image_bytes))
                if image.mode in ("RGBA", "P"):
                    image = image.convert("RGB")
                    
                response = self.model.generate_content([system_prompt, image])
            else:
                response = self.model.generate_content(
                    [system_prompt, f"Text input: {text_input or 'Unknown item'}"]
                )

            raw_text = response.text

            # --- SAFETY CHECK ---
            try:
                ai_data = json.loads(raw_text)
                if ai_data.get("material") == "Invalid" or ai_data.get("item_type") == "Invalid":
                    return {
                        "success": False,
                        "error": "Non-waste item detected (Face/Person/Pet). Please scan actual waste."
                    }
            except Exception:
                pass 

            parsed = self._safe_parse(raw_text, fallback_item_name)
            return {"success": True, "data": parsed}
            
        except Exception as exc:
            log_error(f"Gemini Service Error: {str(exc)}")
            return {"success": True, "data": self.get_fallback(fallback_item_name)}

    def _safe_parse(self, raw_text: str, fallback_item_name: str):
        try:
            parsed = json.loads(raw_text)
        except Exception:
            parsed = {}

        if not isinstance(parsed, dict):
            parsed = {}

        fallback = self.get_fallback(fallback_item_name)

        item_name = str(parsed.get("item_name") or fallback["item_name"])
        material = str(parsed.get("material") or fallback["material"])
        estimated_weight = str(parsed.get("estimated_weight") or fallback["estimated_weight"])

        size = str(parsed.get("size") or fallback["size"]).title()
        if size not in {"Small", "Medium", "Large"}:
            size = fallback["size"]

        # Expanded condition list
        condition = str(parsed.get("condition") or fallback["condition"]).title()
        if condition not in {"Mint", "Good", "Fair", "Poor", "Broken", "Dead", "Clean", "Dirty", "Mixed"}:
            condition = fallback["condition"]

        # Dynamic Question Parsing (Ensures exactly 4 questions)
        questions = parsed.get("verification_questions")
        if not isinstance(questions, list):
            questions = fallback["verification_questions"]
        questions = [str(q).strip() for q in questions if str(q).strip()]
        
        while len(questions) < 4:
            questions.append(fallback["verification_questions"][len(questions) % 4])
        questions = questions[:4]

        return {
            "item_name": item_name,
            "material": material,
            "estimated_weight": estimated_weight,
            "size": size,
            "condition": condition,
            "verification_questions": questions,
        }

    def get_fallback(self, item_name: str):
        return {
            "item_name": item_name or "Scanned Waste Item",
            "material": "Other",
            "estimated_weight": "0.5 kg",
            "size": "Medium",
            "condition": "Mixed",
            "verification_questions": [
                "Approximately what year was this purchased?",
                "Is the item still functional or completely broken?",
                "Has it lost any of its original parts?",
                "Is it heavier than it looks?",
            ],
        }

gemini_service = GeminiService()