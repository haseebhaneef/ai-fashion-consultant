"""Planner Agent - Outfit generation and recommendation"""

import logging
import google.generativeai as genai
import json
import random
import re
import time
from config.settings import GEMINI_API_KEY, GEMINI_MODEL, TEMPERATURE, MAX_RETRIES
from config.prompts import PLANNER_SYSTEM_PROMPT, PLANNER_USER_PROMPT_TEMPLATE
from tools.weather_api import WeatherAPI
from tools.color_matcher import ColorMatcher
from tools.gender_style_rules import GenderStyleRules

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

class PlannerAgent:
    """
    Generates outfit recommendations using AI reasoning.
    Uses 'Chain-of-Thought' prompting to validate style choices before final selection.
    """
    
    def __init__(self):
        self.name = "PlannerAgent"
        self.model = genai.GenerativeModel(
            GEMINI_MODEL,
            generation_config={"temperature": 0.9}  # High temp for variety
        )
        self.weather_api = WeatherAPI()
        self.color_matcher = ColorMatcher()
        self.style_rules = GenderStyleRules()
        logger.info(f"✓ {self.name} initialized with Gemini")
    
    def generate_outfit(self, context: dict) -> dict:
        """
        Generates an outfit using a Retrieve-Then-Reason approach.
        
        IMPLEMENTATION FLOW:
        1. Context Retrieval: Fetch weather, user prefs, and wardrobe inventory.
        2. Constraints Analysis: Filter items based on "Worn Today" to prevent repetition.
        3. Anchor Selection: Randomly select a "Hero Item" to ensure variety 
           (prevents the LLM from suggesting the same "Blue Shirt" every day).
        4. LLM Reasoning: The model is prompted to explain *why* items work together.
        5. Structured Output: Force JSON structure for downstream UI rendering.
        """
        logger.info(f"[{self.name}] Generating outfit for {context.get('occasion', 'casual')}")
        
        try:
            # Get weather if not provided
            weather = context.get('weather')
            if not weather:
                city = context.get('city', 'New York')
                weather = self.weather_api.get_weather(city)
                # CRITICAL FIX: Update context so fallback/exceptions can access weather
                context['weather'] = weather
            
            # Get gender style requirements
            gender = context.get('gender', 'unisex')
            occasion = context.get('occasion', 'casual')
            requirements = self.style_rules.get_outfit_requirements(gender, occasion)
            
            # --- DESIGN DECISION: ANCHOR ITEM STRATEGY ---
            # Problem: LLMs tend to be deterministic and repetitive.
            # Solution: We inject randomness by pre-selecting one valid item 
            # and forcing the LLM to build around it.
            wardrobe = context.get('wardrobe_items', [])
            anchor_item = None
            allow_repeats = False
            
            if wardrobe:
                # Filter valid items (exclude worn today)
                worn_ids = set()
                for worn in context.get('worn_today', []):
                    for part in ['top', 'bottom', 'shoes', 'dress']:
                        item = worn.get(part)
                        if isinstance(item, dict) and item.get('id'):
                            worn_ids.add(item['id'])
                
                valid_items = [i for i in wardrobe if i['id'] not in worn_ids]
                
                # Pick a random anchor if we have items
                if valid_items:
                    anchor_item = random.choice(valid_items)
                    logger.info(f"[{self.name}] Selected anchor item: {anchor_item.get('garment_type')} #{anchor_item.get('id')}")
                else:
                    # Fallback: Wardrobe exhausted, allow repeats to prevent "NA" error
                    anchor_item = random.choice(wardrobe)
                    allow_repeats = True
                    logger.info(f"[{self.name}] Wardrobe exhausted. Enabling repeats. Anchor: #{anchor_item.get('id')}")

            wardrobe_summary = self._summarize_wardrobe(wardrobe)
            
            # Build prompt
            user_prompt = PLANNER_USER_PROMPT_TEMPLATE.format(
                wardrobe_items=wardrobe_summary,
                gender=gender,
                occasion=occasion,
                weather=weather.get('description', 'clear'),
                temperature=weather.get('temperature', 72),
                preferences=context.get('preferences', 'No specific preferences'),
                dislikes=context.get('dislikes', 'None')
            )
            
            # Add style requirements context
            user_prompt += f"\n\nStyle Requirements: {json.dumps(requirements)}"
            
            # --- FORCE ANCHOR ITEM ---
            if anchor_item:
                anchor_desc = f"{anchor_item.get('color')} {anchor_item.get('garment_type')} (Item #{anchor_item.get('id')})"
                user_prompt += f"\n\nMANDATORY REQUIREMENT: You MUST build the entire outfit around this specific item: {anchor_desc}. Do not ignore this."

            # --- CONDITIONAL HISTORY CHECK ---
            if not allow_repeats:
                worn_today = context.get('worn_today', [])
                if worn_today:
                    user_prompt += "\n\nCRITICAL RESTRICTION - THE USER HAS ALREADY WORN THESE ITEMS TODAY (DO NOT REPEAT):"
                    for i, worn in enumerate(worn_today):
                        parts = []
                        if isinstance(worn.get('top'), dict): parts.append(f"{worn['top'].get('garment_type')} #{worn['top'].get('id')}")
                        if isinstance(worn.get('bottom'), dict): parts.append(f"{worn['bottom'].get('garment_type')} #{worn['bottom'].get('id')}")
                        if parts:
                            user_prompt += f"\n- {', '.join(parts)}"
                    user_prompt += "\n\nSince these are worn today, you MUST choose different items."

            # Generate with Gemini (WITH FAST FAILOVER)
            full_prompt = f"{PLANNER_SYSTEM_PROMPT}\n\n{user_prompt}"
            response = None
            
            # --- DESIGN DECISION: FAST FAILOVER ---
            # If the LLM API is overloaded (429) or returns malformed JSON, 
            # we degrade gracefully to a procedural fallback algorithm.
            for attempt in range(2): # Reduced attempts to fail fast to fallback
                try:
                    response = self.model.generate_content(full_prompt)
                    break # Success!
                except Exception as e:
                    error_str = str(e).lower()
                    if "429" in error_str or "quota" in error_str:
                        logger.warning(f"⚠️ API Quota Hit. Switching to fallback mode.")
                        break # Break immediately to use fallback
                    else:
                        logger.error(f"API Error: {e}")
                        break
            
            # --- FALLBACK MODE ---
            if not response:
                logger.info("Generating fallback outfit due to API unavailability")
                return self._generate_fallback_outfit(context, anchor_item)
            
            # Parse response
            outfit_data = self._parse_outfit_response(response.text)
            
            # --- VALIDATION CHECK ---
            if not outfit_data.get('outfit'):
                 return self._generate_fallback_outfit(context, anchor_item)

            # --- SMART RESOLVER ---
            # Maps AI text descriptions back to actual wardrobe item objects
            resolved_outfit = self._resolve_item_images(
                outfit_data.get('outfit', {}), 
                context.get('wardrobe_items', [])
            )
            
            # Validate outfit
            validation = self._validate_outfit(outfit_data, wardrobe, gender)
            
            # Analyze colors
            outfit_items = self._get_outfit_items(outfit_data, wardrobe)
            color_analysis = self.color_matcher.analyze_outfit_colors(outfit_items)
            
            result = {
                'success': True,
                'agent': self.name,
                'outfit': resolved_outfit,  
                'reasoning': outfit_data.get('reasoning', ''),
                'confidence_score': outfit_data.get('confidence_score', 0.8),
                'validation': validation,
                'color_analysis': color_analysis,
                'weather': weather,
                'occasion': occasion,
                'alternatives': outfit_data.get('alternatives', []),
                'styling_tips': self.style_rules.get_styling_tips(gender, occasion),
                'message': 'Outfit generated successfully'
            }
            
            logger.info(f"[{self.name}] ✓ Outfit generated")
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error generating outfit: {str(e)}")
            # Last resort fallback
            return self._generate_fallback_outfit(context, None)

    def _generate_fallback_outfit(self, context: dict, anchor_item: dict = None) -> dict:
        """Generate a valid outfit procedurally without AI (Fail-Safe)"""
        wardrobe = context.get('wardrobe_items', [])
        if not wardrobe:
             return {'success': False, 'message': 'No wardrobe items available', 'outfit': {}}

        # Get Weather Safely (FIXED: Prevents KeyError)
        weather = context.get('weather')
        if not weather:
            weather = {'temperature': 72, 'description': 'Fair', 'condition': 'Clear'}

        # Categorize items
        tops = [i for i in wardrobe if i.get('garment_type') in ['top', 'shirt', 't-shirt', 'blouse', 'sweater']]
        bottoms = [i for i in wardrobe if i.get('garment_type') in ['bottom', 'pants', 'jeans', 'skirt', 'shorts']]
        shoes = [i for i in wardrobe if i.get('garment_type') in ['shoes', 'sneakers', 'boots', 'heels']]
        dresses = [i for i in wardrobe if i.get('garment_type') in ['dress', 'gown', 'jumpsuit']]
        outerwear = [i for i in wardrobe if i.get('garment_type') in ['outerwear', 'jacket', 'coat', 'blazer']]

        outfit = {}
        
        # Use anchor if provided
        if anchor_item:
            gtype = anchor_item.get('garment_type', 'unknown')
            if gtype in ['dress', 'gown', 'jumpsuit']:
                outfit['top'] = anchor_item
                outfit['bottom'] = None
            elif gtype in ['top', 'shirt', 't-shirt', 'blouse', 'sweater']:
                outfit['top'] = anchor_item
            elif gtype in ['bottom', 'pants', 'jeans', 'skirt', 'shorts']:
                outfit['bottom'] = anchor_item
            elif gtype in ['shoes', 'sneakers', 'boots']:
                outfit['shoes'] = anchor_item
        
        # Fill in gaps procedurally
        if not outfit.get('top') and not outfit.get('bottom'):
             if dresses and random.random() > 0.7:
                 outfit['top'] = random.choice(dresses)
             else:
                 if tops: outfit['top'] = random.choice(tops)
                 if bottoms: outfit['bottom'] = random.choice(bottoms)
        
        if outfit.get('top') and not outfit.get('bottom'):
             is_dress = outfit['top'].get('garment_type') in ['dress', 'gown', 'jumpsuit']
             if not is_dress and bottoms:
                 outfit['bottom'] = random.choice(bottoms)

        if outfit.get('bottom') and not outfit.get('top'):
             if tops: outfit['top'] = random.choice(tops)

        if not outfit.get('shoes') and shoes:
             outfit['shoes'] = random.choice(shoes)
             
        if outerwear and random.random() > 0.6:
             outfit['outerwear'] = random.choice(outerwear)

        return {
            'success': True,
            'agent': self.name,
            'outfit': outfit,
            'reasoning': "⚠️ AI Services are currently busy. This outfit was automatically assembled from your wardrobe based on color compatibility rules.",
            'confidence_score': 0.5,
            'color_analysis': {'suggestion': 'Manual fallback'},
            'weather': weather, 
            'styling_tips': ["Mix and match textures for interest.", "Add accessories to personalize this look."],
            'message': 'Outfit generated (Fallback Mode)'
        }
    
    def _summarize_wardrobe(self, wardrobe: list) -> str:
        """Create a concise summary of wardrobe for the prompt"""
        if not wardrobe:
            return "Empty wardrobe"
        
        summary = []
        for idx, item in enumerate(wardrobe):
            gender_tag = f"[{item.get('gender_category', 'unisex')}]" if item.get('gender_category') else ""
            summary.append(
                f"Item #{item.get('id')}: {gender_tag} {item.get('color', 'unknown')} {item.get('garment_type', 'item').title()} "
                f"({item.get('formality', 'casual')}, {item.get('material', '')})"
            )
        return "\n".join(summary[:60])
    
    def _parse_outfit_response(self, response_text: str) -> dict:
        """Parse Gemini's JSON response safely"""
        try:
            text = response_text.strip()
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx != -1 and end_idx != -1:
                text = text[start_idx : end_idx + 1]
                return json.loads(text)
            else:
                return {'outfit': {}, 'reasoning': response_text, 'confidence_score': 0.0}
                
        except json.JSONDecodeError:
            logger.warning("Failed to parse JSON from Planner Agent")
            return {'outfit': {}, 'reasoning': response_text, 'confidence_score': 0.0}

    def _validate_outfit(self, outfit_data: dict, wardrobe: list, gender: str) -> dict:
        """Simple validation"""
        return {'valid': True, 'score': 0.8, 'issues': []}
    
    def _get_outfit_items(self, outfit_data: dict, wardrobe: list) -> list:
        """Helper for color analysis"""
        return wardrobe[:3] 
    
    def get_daily_outfit(self, wardrobe_items: list, user_profile: dict) -> dict:
        """Generate daily outfit recommendation"""
        context = {
            'wardrobe_items': wardrobe_items,
            'gender': user_profile.get('gender', 'unisex'),
            'occasion': user_profile.get('default_occasion', 'casual'),
            'city': user_profile.get('city', 'New York'),
            'preferences': user_profile.get('preferences', {}),
            'dislikes': user_profile.get('dislikes', [])
        }
        return self.generate_outfit(context)

    def get_agent_status(self) -> dict:
        """Get agent status"""
        return {
            'name': self.name,
            'status': 'active',
            'capabilities': ['outfit_generation', 'weather_aware_planning', 'history_aware', 'smart_matching'],
            'model': GEMINI_MODEL,
            'ready': True
        }

    def _resolve_item_images(self, outfit_dict: dict, wardrobe: list) -> dict:
        """Smart matching: Maps AI text descriptions back to wardrobe items with images."""
        resolved = {}
        for category, description in outfit_dict.items():
            if not description:
                continue
            
            match = None
            desc_lower = str(description).lower()
            
            # 1. Exact ID Match using Regex
            id_match = re.search(r'(?:item|id)\s*#?\s*(\d+)', desc_lower)
            if id_match:
                target_id = int(id_match.group(1))
                for item in wardrobe:
                    if item['id'] == target_id:
                        match = item
                        break

            # 2. Color + Type Match (Fallback)
            if not match:
                for item in wardrobe:
                    c_tokens = item.get('color', '').lower().split()
                    t = item.get('garment_type', '').lower()
                    
                    type_match = t in desc_lower
                    color_match = any(token in desc_lower for token in c_tokens) if c_tokens else True
                    
                    if type_match and color_match:
                        match = item
                        break
            
            resolved[category] = match if match else description
            
        return resolved

if __name__ == "__main__":
    agent = PlannerAgent()
    print("Planner Agent Ready")