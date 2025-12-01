"""Recommender Agent - Purchase recommendations and wardrobe gap analysis"""

import logging
import google.generativeai as genai
import json
from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from config.prompts import RECOMMENDER_SYSTEM_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)

class RecommenderAgent:
    """
    Analyzes wardrobe gaps and suggests smart purchases
    Identifies missing essentials and high-impact additions
    """
    
    def __init__(self):
        self.name = "RecommenderAgent"
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        logger.info(f"✓ {self.name} initialized")
    
    def analyze_wardrobe_gaps(self, wardrobe_items: list, user_profile: dict) -> dict:
        """
        Analyze wardrobe and identify gaps
        
        Args:
            wardrobe_items: Current wardrobe
            user_profile: User preferences and needs
            
        Returns:
            dict: Gap analysis and recommendations
        """
        logger.info(f"[{self.name}] Analyzing wardrobe gaps")
        
        try:
            # Summarize wardrobe
            wardrobe_summary = self._create_wardrobe_summary(wardrobe_items)
            
            # Build prompt
            prompt = f"""{RECOMMENDER_SYSTEM_PROMPT}

Analyze this wardrobe and provide recommendations:

Current Wardrobe:
{wardrobe_summary}

User Profile:
- Gender: {user_profile.get('gender', 'unisex')}
- Occasions: {', '.join(user_profile.get('occasions', ['casual', 'work']))}
- Preferred Colors: {', '.join(user_profile.get('favorite_colors', []))}
- Budget Range: {user_profile.get('budget', 'moderate')}

Provide 3-5 strategic purchase recommendations that would maximize outfit possibilities."""

            # Generate recommendations
            response = self.model.generate_content(prompt)
            recommendations_data = self._parse_recommendations(response.text)
            
            # Calculate coverage score
            coverage_score = self._calculate_coverage(wardrobe_items, user_profile)
            
            result = {
                'success': True,
                'agent': self.name,
                'recommendations': recommendations_data.get('recommendations', []),
                'wardrobe_analysis': {
                    'total_items': len(wardrobe_items),
                    'coverage_score': coverage_score,
                    'gaps_identified': len(recommendations_data.get('recommendations', [])),
                    'missing_categories': recommendations_data.get('missing_categories', [])
                },
                'message': f"Found {len(recommendations_data.get('recommendations', []))} recommendations"
            }
            
            logger.info(f"[{self.name}] ✓ Gap analysis complete: {coverage_score:.0%} coverage")
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error analyzing gaps: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'recommendations': [],
                'message': f"Error: {str(e)}"
            }
    
    def suggest_purchases(self, occasion: str, wardrobe_items: list) -> dict:
        """
        Suggest purchases for a specific occasion
        
        Args:
            occasion: Target occasion
            wardrobe_items: Current wardrobe
            
        Returns:
            dict: Occasion-specific recommendations
        """
        logger.info(f"[{self.name}] Generating purchase suggestions for {occasion}")
        
        try:
            wardrobe_summary = self._create_wardrobe_summary(wardrobe_items)
            
            prompt = f"""Analyze this wardrobe for a {occasion} occasion:

{wardrobe_summary}

What 2-3 items should be purchased to create great {occasion} outfits?
Return JSON with recommendations including item type, color, why it's needed, and price range."""

            response = self.model.generate_content(prompt)
            recommendations = self._parse_recommendations(response.text)
            
            return {
                'success': True,
                'agent': self.name,
                'occasion': occasion,
                'recommendations': recommendations.get('recommendations', []),
                'message': f"Generated {occasion} recommendations"
            }
            
        except Exception as e:
            logger.error(f"[{self.name}] Error: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'recommendations': [],
                'message': f"Error: {str(e)}"
            }
    
    def _create_wardrobe_summary(self, wardrobe: list) -> str:
        """Create summary of wardrobe for analysis"""
        if not wardrobe:
            return "Empty wardrobe - needs foundational pieces"
        
        # Count by type
        type_counts = {}
        for item in wardrobe:
            item_type = item.get('garment_type', 'unknown')
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        summary = [f"Total Items: {len(wardrobe)}\n"]
        summary.append("By Category:")
        for item_type, count in sorted(type_counts.items()):
            summary.append(f"  - {item_type.title()}: {count}")
        
        # Add color distribution
        colors = [item.get('color', 'unknown') for item in wardrobe]
        color_counts = {}
        for color in colors:
            color_counts[color] = color_counts.get(color, 0) + 1
        
        summary.append("\nColors:")
        for color, count in sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            summary.append(f"  - {color.title()}: {count}")
        
        return "\n".join(summary)
    
    def _parse_recommendations(self, response_text: str) -> dict:
        """Parse recommendations from response"""
        try:
            text = response_text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            data = json.loads(text.strip())
            
            # FIXED: Handle case where model returns a list directly
            if isinstance(data, list):
                return {'recommendations': data}
                
            return data
            
        except json.JSONDecodeError:
            # Fallback: extract recommendations from text
            logger.warning("Failed to parse JSON, using text fallback")
            return {
                'recommendations': [
                    {
                        'item_type': 'Essential pieces',
                        'reason': response_text[:200],
                        'priority': 'high'
                    }
                ],
                'missing_categories': []
            }
    
    def _calculate_coverage(self, wardrobe: list, user_profile: dict) -> float:
        """Calculate wardrobe coverage score"""
        if not wardrobe:
            return 0.0
        
        # Essential categories
        essentials = {
            'shirt': 3,
            'pants': 2,
            'shoes': 2,
            'outerwear': 1
        }
        
        # Count coverage
        type_counts = {}
        for item in wardrobe:
            item_type = item.get('garment_type', '')
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        coverage = 0
        for category, minimum in essentials.items():
            coverage += min(1.0, type_counts.get(category, 0) / minimum)
        
        return coverage / len(essentials)
    
    def get_agent_status(self) -> dict:
        """Get agent status"""
        return {
            'name': self.name,
            'status': 'active',
            'capabilities': [
                'gap_analysis',
                'purchase_recommendations',
                'coverage_calculation',
                'occasion_planning',
                'wardrobe_optimization'
            ],
            'model': GEMINI_MODEL,
            'ready': True
        }


# Test
if __name__ == "__main__":
    agent = RecommenderAgent()
    print(agent.get_agent_status())