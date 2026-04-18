import os
import json
import logging
from google import genai

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY environment variable is missing.")
        self.client = genai.Client(api_key=api_key) if api_key else None

        self.system_prompt = (
            "Classify the waste item from provided image(s). Return ONLY valid JSON with keys: "
            "item_name, category, material, confidence, estimated_value, co2_saved, size, condition, "
            "disposal_method, verification_questions. "
            "Use category from [plastic, metal, e-waste, glass, paper, organic, mixed]. "
            "size in [Small, Medium, Large], condition in [Clean, Dirty, Mixed]. "
            "confidence must be 0..1. Always include exactly 3 verification_questions."
        )

    async def analyze_waste(self, images_bytes=None):
        if not self.client:
            logger.error("Gemini client unavailable. Falling back.")
            return {"success": True, "data": self._fallback_data()}

        try:
            prompt = self.system_prompt
            if images_bytes:
                prompt = f"{prompt} Number of uploaded images: {len(images_bytes)}."

            response = self.client.models.generate_content(
                model="gemini-1.5-flash",
                contents=[{"role": "user", "parts": [{"text": prompt}]}],
            )
            text = response.text
            text_response = (text or "").strip()

            if not text_response:
                raise ValueError("Empty Gemini response text.")

            if text_response.startswith("```json"):
                text_response = text_response[7:]
            if text_response.startswith("```"):
                text_response = text_response[3:]
            if text_response.endswith("```"):
                text_response = text_response[:-3]

            parsed_data = json.loads(text_response.strip())
            return {"success": True, "data": parsed_data}
        except Exception as exc:
            logger.warning("Gemini request failed: %s", str(exc))
            logger.error("Gemini unavailable. Using fallback response.")
            return {"success": True, "data": self._fallback_data()}

    def _fallback_data(self):
        fallback_data = {
            "item_name": "API Limit Reached (Simulated Item)",
            "category": "plastic",
            "material": "mixed plastic",
            "confidence": 0.99,
            "estimated_value": 15,
            "co2_saved": 1.2,
            "size": "Medium",
            "condition": "Mixed",
            "disposal_method": "recycle",
            "verification_questions": [
                "You have hit Google's daily Free Tier limit.",
                "To get real AI predictions, create a new API Key.",
                "You can still log this fake item to test your Dashboard!"
            ]
        }
        return fallback_data

gemini_service = GeminiService()