"""Gender-aware styling rules"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenderStyleRules:
    """Apply gender-specific styling rules"""
    
    def __init__(self):
        self.rules = {
            'male': {
                'required_categories': ['top', 'bottom', 'shoes'],
                'optional_categories': ['outerwear', 'accessories'],
                'formality_mapping': {
                    'casual': ['t-shirt', 'jeans', 'sneakers'],
                    'business_casual': ['button-down', 'chinos', 'loafers'],
                    'formal': ['dress_shirt', 'suit_pants', 'dress_shoes']
                },
                'layering_order': ['undershirt', 'shirt', 'sweater', 'jacket', 'coat'],
                'accessory_limits': 3
            },
            'female': {
                'required_categories': ['top_or_dress', 'bottom_optional', 'shoes'],
                'optional_categories': ['outerwear', 'accessories', 'jewelry'],
                'formality_mapping': {
                    'casual': ['t-shirt', 'jeans', 'sneakers', 'sundress'],
                    'business_casual': ['blouse', 'skirt', 'heels', 'blazer'],
                    'formal': ['dress', 'heels', 'evening_wear']
                },
                'layering_order': ['dress/top', 'cardigan', 'blazer', 'coat'],
                'accessory_limits': 5
            },
            'unisex': {
                'required_categories': ['top', 'bottom', 'shoes'],
                'optional_categories': ['outerwear', 'accessories'],
                'formality_mapping': {
                    'casual': ['t-shirt', 'jeans', 'sneakers'],
                    'business_casual': ['shirt', 'pants', 'shoes'],
                    'formal': ['formal_top', 'formal_bottom', 'formal_shoes']
                },
                'layering_order': ['base', 'mid', 'outer'],
                'accessory_limits': 4
            }
        }
    
    def get_outfit_requirements(self, gender: str, occasion: str) -> dict:
        """
        Get outfit requirements for gender and occasion
        
        Args:
            gender: male/female/unisex
            occasion: casual/work/formal/etc
            
        Returns:
            dict: Outfit requirements
        """
        gender = gender.lower()
        if gender not in self.rules:
            gender = 'unisex'
        
        rules = self.rules[gender]
        
        # Map occasion to formality
        formality_map = {
            'casual': 'casual',
            'work': 'business_casual',
            'business': 'business_casual',
            'formal': 'formal',
            'wedding': 'formal',
            'party': 'business_casual',
            'date': 'business_casual'
        }
        
        formality = formality_map.get(occasion, 'casual')
        
        return {
            'gender': gender,
            'occasion': occasion,
            'formality': formality,
            'required_categories': rules['required_categories'],
            'optional_categories': rules['optional_categories'],
            'suggested_items': rules['formality_mapping'].get(formality, []),
            'max_accessories': rules['accessory_limits'],
            'layering_order': rules['layering_order']
        }
    
    def validate_outfit(self, outfit: dict, gender: str) -> dict:
        """
        Validate if outfit meets gender-specific requirements
        
        Args:
            outfit: Outfit dictionary
            gender: Gender profile
            
        Returns:
            dict: Validation result
        """
        gender = gender.lower()
        if gender not in self.rules:
            gender = 'unisex'
        
        rules = self.rules[gender]
        required = rules['required_categories']
        
        # Check required items
        missing = []
        for category in required:
            if category == 'top_or_dress':
                if not (outfit.get('top') or outfit.get('dress')):
                    missing.append('top or dress')
            elif category == 'bottom_optional':
                # Optional for dresses
                if not outfit.get('dress') and not outfit.get('bottom'):
                    missing.append('bottom (unless wearing dress)')
            else:
                if not outfit.get(category):
                    missing.append(category)
        
        # Check accessory limits
        accessories = outfit.get('accessories', [])
        if len(accessories) > rules['accessory_limits']:
            return {
                'valid': False,
                'score': 0.6,
                'issues': [f"Too many accessories ({len(accessories)} > {rules['accessory_limits']})"],
                'missing': missing
            }
        
        if missing:
            return {
                'valid': False,
                'score': 0.3,
                'issues': [f"Missing required items: {', '.join(missing)}"],
                'missing': missing
            }
        
        return {
            'valid': True,
            'score': 1.0,
            'issues': [],
            'missing': []
        }
    
    def get_styling_tips(self, gender: str, occasion: str) -> list:
        """Get styling tips for gender and occasion"""
        tips = {
            'male': {
                'casual': [
                    "Fit is key - even casual wear should fit well",
                    "Dark jeans are more versatile than light wash",
                    "White sneakers go with almost everything"
                ],
                'work': [
                    "Match your belt to your shoes",
                    "Keep shirts tucked for a polished look",
                    "Avoid overly bold patterns in professional settings"
                ],
                'formal': [
                    "Suit should be tailored to your body",
                    "Tie should reach your belt buckle",
                    "Dress shoes should be polished"
                ]
            },
            'female': {
                'casual': [
                    "Layer pieces for versatility",
                    "Comfortable shoes are essential",
                    "Statement accessory can elevate simple outfit"
                ],
                'work': [
                    "Classic pieces create a professional wardrobe",
                    "Neutral colors are easiest to mix and match",
                    "Keep jewelry minimal and elegant"
                ],
                'formal': [
                    "Dress should fit perfectly - consider tailoring",
                    "Coordinate heel height with dress length",
                    "Less is more with evening accessories"
                ]
            }
        }
        
        gender = gender.lower()
        if gender not in tips:
            gender = 'male'
        
        occasion_map = {
            'casual': 'casual',
            'work': 'work',
            'business': 'work',
            'formal': 'formal',
            'wedding': 'formal',
            'party': 'formal'
        }
        
        occasion_key = occasion_map.get(occasion, 'casual')
        return tips[gender].get(occasion_key, [])


# Test
if __name__ == "__main__":
    rules = GenderStyleRules()
    
    # Get requirements
    reqs = rules.get_outfit_requirements('female', 'work')
    print(f"Female work outfit requirements: {reqs}")
    
    # Validate outfit
    outfit = {'top': 'blouse', 'bottom': 'skirt', 'shoes': 'heels'}
    validation = rules.validate_outfit(outfit, 'female')
    print(f"Outfit validation: {validation}")
    
    # Get tips
    tips = rules.get_styling_tips('male', 'formal')
    print(f"Styling tips: {tips}")