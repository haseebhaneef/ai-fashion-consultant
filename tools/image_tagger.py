"""Image tagging tool using Gemini Vision"""

import google.generativeai as genai
from PIL import Image
import json
import logging
import time
import re
from config.settings import GEMINI_API_KEY, GEMINI_VISION_MODEL, MAX_RETRIES
from config.prompts import PERCEPTION_SYSTEM_PROMPT, PERCEPTION_USER_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

class ImageTagger:
    """Tags clothing items using Gemini Vision"""
    
    def __init__(self):
        self.model = genai.GenerativeModel(GEMINI_VISION_MODEL)
        logger.info("ImageTagger initialized with Gemini Vision")
    
    def tag_garment(self, image_path: str) -> dict:
        """
        Analyze clothing image and extract attributes
        
        Args:
            image_path: Path to clothing image
            
        Returns:
            dict: Garment attributes
        """
        for attempt in range(MAX_RETRIES):
            try:
                # Load image
                img = Image.open(image_path)
                
                # Create prompt
                prompt = f"{PERCEPTION_SYSTEM_PROMPT}\n\n{PERCEPTION_USER_PROMPT}"
                
                # Generate response
                response = self.model.generate_content([prompt, img])
                
                # Parse JSON response
                response_text = response.text.strip()
                
                # Robust JSON extraction (Find first { and last })
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}')
                
                if start_idx != -1 and end_idx != -1:
                    clean_json = response_text[start_idx : end_idx + 1]
                    tags = json.loads(clean_json)
                else:
                    # Fallback cleanup if braces aren't found (rare)
                    clean_json = response_text.replace("```json", "").replace("```", "").strip()
                    tags = json.loads(clean_json)
                
                # Add metadata
                tags['image_path'] = image_path
                tags['tagged_by'] = 'gemini-vision'
                
                logger.info(f"✓ Tagged {image_path}: {tags.get('garment_type', 'unknown')}")
                return tags
                
            except Exception as e:
                logger.warning(f"⚠️ Attempt {attempt+1}/{MAX_RETRIES} failed for {image_path}: {str(e)}")
                
                # If this was the last attempt, return fallback
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"✗ Error tagging {image_path} after retries: {str(e)}")
                    return self._fallback_tags(image_path, str(e))
                
                # Wait before retrying (Exponential backoff: 2s, 4s, 8s...)
                time.sleep(2 ** (attempt + 1))
    
    def _fallback_tags(self, image_path: str, error: str) -> dict:
        """Return fallback tags when vision fails"""
        return {
            "garment_type": "unknown",
            "gender_category": "unisex", # Default
            "color": "unknown",
            "secondary_colors": [],
            "pattern": "unknown",
            "formality": "casual",
            "season": ["spring", "summer", "fall", "winter"],
            "material": "unknown",
            "style_tags": [],
            "brand": None,
            "condition": "good",
            "image_path": image_path,
            "tagged_by": "fallback",
            "error": error
        }
    
    def batch_tag(self, image_paths: list) -> list:
        """Tag multiple images"""
        results = []
        for path in image_paths:
            tags = self.tag_garment(path)
            results.append(tags)
            # Small delay between batch items handled in orchestrator/perception agent
        return results


# Test function
if __name__ == "__main__":
    tagger = ImageTagger()
    # Test with sample image
    print("ImageTagger ready for use")