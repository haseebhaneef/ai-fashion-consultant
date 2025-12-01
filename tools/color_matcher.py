"""Color matching and harmony tool"""

import logging
from config.settings import COLOR_COMPLEMENTARY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ColorMatcher:
    """Validates color combinations using color theory"""
    
    def __init__(self):
        self.complementary = COLOR_COMPLEMENTARY
    
    def validate_combination(self, colors: list) -> dict:
        """
        Check if color combination works
        
        Args:
            colors: List of color names
            
        Returns:
            dict: Validation result with score and reasoning
        """
        if not colors or len(colors) < 2:
            return {
                'valid': True,
                'score': 1.0,
                'reasoning': 'Single or no colors - automatically valid'
            }
        
        # Normalize colors
        colors = [c.lower() for c in colors]
        
        # Check if neutral colors present (always work)
        neutrals = {'white', 'black', 'gray', 'grey', 'beige', 'cream', 'navy', 'brown'}
        has_neutral = any(c in neutrals for c in colors)
        
        if has_neutral:
            return {
                'valid': True,
                'score': 0.95,
                'reasoning': 'Contains neutral colors which pair well with most colors'
            }
        
        # Check complementary colors
        primary = colors[0]
        secondary = colors[1:]
        
        if primary in self.complementary:
            complements = self.complementary[primary]
            
            if 'any' in complements:
                return {
                    'valid': True,
                    'score': 1.0,
                    'reasoning': f'{primary.title()} is a neutral that works with any color'
                }
            
            # Check how many secondary colors complement primary
            matching = sum(1 for c in secondary if any(comp in c for comp in complements))
            score = matching / len(secondary) if secondary else 1.0
            
            if score >= 0.5:
                return {
                    'valid': True,
                    'score': score,
                    'reasoning': f'{primary.title()} complements well with {", ".join(secondary)}'
                }
            else:
                return {
                    'valid': False,
                    'score': score,
                    'reasoning': f'Warning: {primary.title()} may clash with {", ".join(secondary)}. Consider adding neutrals.'
                }
        
        # Unknown color - be permissive
        return {
            'valid': True,
            'score': 0.7,
            'reasoning': 'Color combination not in database - proceed with caution'
        }
    
    def suggest_matching_colors(self, base_color: str) -> list:
        """Suggest colors that match a base color"""
        base_color = base_color.lower()
        
        if base_color in self.complementary:
            matches = self.complementary[base_color]
            if 'any' in matches:
                return ['white', 'black', 'gray', 'navy', 'beige']
            return matches
        
        # Default neutrals
        return ['white', 'black', 'gray', 'navy']
    
    def analyze_outfit_colors(self, outfit_items: list) -> dict:
        """
        Analyze all colors in an outfit
        
        Args:
            outfit_items: List of items with 'color' field
            
        Returns:
            dict: Analysis with validation and suggestions
        """
        colors = [item.get('color') for item in outfit_items if item.get('color')]
        
        validation = self.validate_combination(colors)
        
        analysis = {
            'colors_used': colors,
            'validation': validation,
            'color_count': len(colors),
            'has_neutral': any(c.lower() in {'white', 'black', 'gray', 'beige'} for c in colors)
        }
        
        if not validation['valid']:
            # Suggest a neutral to add
            analysis['suggestion'] = 'Consider adding a neutral piece (white, black, or gray) to balance the outfit'
        
        return analysis


# Test
if __name__ == "__main__":
    matcher = ColorMatcher()
    
    # Test 1: Good combination
    result = matcher.validate_combination(['blue', 'white'])
    print(f"Blue + White: {result}")
    
    # Test 2: Potentially clashing
    result = matcher.validate_combination(['red', 'orange'])
    print(f"Red + Orange: {result}")
    
    # Test 3: Get suggestions
    suggestions = matcher.suggest_matching_colors('navy')
    print(f"Colors that match navy: {suggestions}")