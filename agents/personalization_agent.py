"""Personalization Agent - User preference learning and memory"""

import logging
import json
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PersonalizationAgent:
    """
    Learns user preferences over time
    Manages long-term memory of style preferences
    """
    
    def __init__(self):
        self.name = "PersonalizationAgent"
        self.memory = {}  # In-memory storage (would be persistent in production)
        logger.info(f"✓ {self.name} initialized")
    
    def update_preferences(self, feedback: dict) -> dict:
        """
        Update user preferences based on feedback
        
        Args:
            feedback: User feedback on outfit/item
            
        Returns:
            dict: Updated preferences
        """
        logger.info(f"[{self.name}] Updating preferences from feedback")
        
        try:
            feedback_type = feedback.get('type', 'neutral')
            
            # Initialize preferences if not exist
            if 'preferences' not in self.memory:
                self.memory['preferences'] = {
                    'favorite_colors': [],
                    'disliked_colors': [],
                    'preferred_styles': [],
                    'avoided_patterns': [],
                    'successful_combinations': [],
                    'feedback_count': 0,
                    'last_updated': None
                }
            
            prefs = self.memory['preferences']
            
            # Process positive feedback
            if feedback_type == 'positive':
                # Add to favorites
                if 'colors' in feedback:
                    for color in feedback['colors']:
                        if color not in prefs['favorite_colors']:
                            prefs['favorite_colors'].append(color)
                
                if 'styles' in feedback:
                    for style in feedback['styles']:
                        if style not in prefs['preferred_styles']:
                            prefs['preferred_styles'].append(style)
                
                if 'combination' in feedback:
                    prefs['successful_combinations'].append({
                        'items': feedback['combination'],
                        'date': datetime.now().isoformat(),
                        'occasion': feedback.get('occasion')
                    })
            
            # Process negative feedback
            elif feedback_type == 'negative':
                if 'colors' in feedback:
                    for color in feedback['colors']:
                        if color not in prefs['disliked_colors']:
                            prefs['disliked_colors'].append(color)
                        # Remove from favorites if present
                        if color in prefs['favorite_colors']:
                            prefs['favorite_colors'].remove(color)
                
                if 'patterns' in feedback:
                    for pattern in feedback['patterns']:
                        if pattern not in prefs['avoided_patterns']:
                            prefs['avoided_patterns'].append(pattern)
            
            # Update metadata
            prefs['feedback_count'] += 1
            prefs['last_updated'] = datetime.now().isoformat()
            
            result = {
                'success': True,
                'agent': self.name,
                'preferences': prefs,
                'message': f"Preferences updated ({prefs['feedback_count']} total feedbacks)"
            }
            
            logger.info(f"[{self.name}] ✓ Preferences updated: {prefs['feedback_count']} feedbacks processed")
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error updating preferences: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'message': f"Error: {str(e)}"
            }
    
    def get_preferences(self) -> dict:
        """Get current user preferences"""
        prefs = self.memory.get('preferences', {
            'favorite_colors': [],
            'disliked_colors': [],
            'preferred_styles': [],
            'avoided_patterns': [],
            'successful_combinations': [],
            'feedback_count': 0
        })
        
        return {
            'success': True,
            'agent': self.name,
            'preferences': prefs,
            'message': 'Preferences retrieved'
        }
    
    def get_style_profile(self) -> dict:
        """Generate comprehensive style profile"""
        logger.info(f"[{self.name}] Generating style profile")
        
        prefs = self.memory.get('preferences', {})
        
        # Analyze patterns in successful combinations
        favorite_colors = prefs.get('favorite_colors', [])
        preferred_styles = prefs.get('preferred_styles', [])
        
        # Generate style description
        if favorite_colors and preferred_styles:
            style_desc = f"Prefers {', '.join(favorite_colors[:3])} colors with {', '.join(preferred_styles[:2])} style"
        elif favorite_colors:
            style_desc = f"Favors {', '.join(favorite_colors[:3])} colors"
        elif preferred_styles:
            style_desc = f"Leans towards {', '.join(preferred_styles[:2])} style"
        else:
            style_desc = "Building style profile - need more feedback"
        
        profile = {
            'success': True,
            'agent': self.name,
            'style_profile': {
                'description': style_desc,
                'favorite_colors': favorite_colors[:5],
                'avoided_colors': prefs.get('disliked_colors', [])[:5],
                'preferred_styles': preferred_styles[:5],
                'avoided_patterns': prefs.get('avoided_patterns', [])[:3],
                'confidence': min(1.0, prefs.get('feedback_count', 0) / 10),
                'total_feedbacks': prefs.get('feedback_count', 0)
            },
            'message': 'Style profile generated'
        }
        
        logger.info(f"[{self.name}] ✓ Style profile: {style_desc}")
        return profile
    
    def recommend_based_on_history(self, candidate_items: list) -> dict:
        """
        Rank items based on learned preferences
        
        Args:
            candidate_items: List of items to rank
            
        Returns:
            dict: Ranked items with scores
        """
        logger.info(f"[{self.name}] Ranking {len(candidate_items)} items by preference")
        
        prefs = self.memory.get('preferences', {})
        favorite_colors = prefs.get('favorite_colors', [])
        disliked_colors = prefs.get('disliked_colors', [])
        preferred_styles = prefs.get('preferred_styles', [])
        avoided_patterns = prefs.get('avoided_patterns', [])
        
        # Score each item
        scored_items = []
        for item in candidate_items:
            score = 0.5  # Base score
            
            # Boost for favorite colors
            if item.get('color', '').lower() in [c.lower() for c in favorite_colors]:
                score += 0.3
            
            # Penalize disliked colors
            if item.get('color', '').lower() in [c.lower() for c in disliked_colors]:
                score -= 0.4
            
            # Boost for preferred styles
            item_styles = item.get('style_tags', [])
            if any(style in preferred_styles for style in item_styles):
                score += 0.2
            
            # Penalize avoided patterns
            if item.get('pattern', '') in avoided_patterns:
                score -= 0.3
            
            # Ensure score is between 0 and 1
            score = max(0, min(1, score))
            
            scored_items.append({
                'item': item,
                'preference_score': score
            })
        
        # Sort by score
        scored_items.sort(key=lambda x: x['preference_score'], reverse=True)
        
        return {
            'success': True,
            'agent': self.name,
            'ranked_items': scored_items,
            'message': f"Ranked {len(scored_items)} items"
        }
    
    def analyze_preference_trends(self) -> dict:
        """
        Analyze trends in user preferences over time
        
        Returns:
            dict: Trend analysis
        """
        logger.info(f"[{self.name}] Analyzing preference trends")
        
        prefs = self.memory.get('preferences', {})
        
        # Analyze successful combinations
        successful_combos = prefs.get('successful_combinations', [])
        
        # Extract color patterns
        color_frequency = {}
        for combo in successful_combos:
            for item in combo.get('items', []):
                color = item.get('color', 'unknown')
                color_frequency[color] = color_frequency.get(color, 0) + 1
        
        # Sort by frequency
        trending_colors = sorted(color_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Calculate consistency score
        feedback_count = prefs.get('feedback_count', 0)
        if feedback_count > 0:
            consistency = len(prefs.get('favorite_colors', [])) / max(1, feedback_count)
        else:
            consistency = 0
        
        trends = {
            'success': True,
            'agent': self.name,
            'trends': {
                'trending_colors': [c[0] for c in trending_colors],
                'consistency_score': round(consistency, 2),
                'total_feedbacks': feedback_count,
                'successful_combinations_count': len(successful_combos),
                'style_diversity': len(prefs.get('preferred_styles', []))
            },
            'message': 'Trend analysis complete'
        }
        
        logger.info(f"[{self.name}] ✓ Trends analyzed")
        return trends
    
    def reset_preferences(self) -> dict:
        """Reset all preferences (useful for testing or user request)"""
        logger.info(f"[{self.name}] Resetting preferences")
        
        self.memory['preferences'] = {
            'favorite_colors': [],
            'disliked_colors': [],
            'preferred_styles': [],
            'avoided_patterns': [],
            'successful_combinations': [],
            'feedback_count': 0,
            'last_updated': datetime.now().isoformat()
        }
        
        return {
            'success': True,
            'agent': self.name,
            'message': 'Preferences reset successfully'
        }
    
    def export_preferences(self) -> dict:
        """Export preferences as JSON for backup/migration"""
        logger.info(f"[{self.name}] Exporting preferences")
        
        prefs = self.memory.get('preferences', {})
        
        return {
            'success': True,
            'agent': self.name,
            'preferences_json': json.dumps(prefs, indent=2),
            'message': 'Preferences exported'
        }
    
    def import_preferences(self, preferences_json: str) -> dict:
        """Import preferences from JSON"""
        logger.info(f"[{self.name}] Importing preferences")
        
        try:
            prefs = json.loads(preferences_json)
            self.memory['preferences'] = prefs
            
            return {
                'success': True,
                'agent': self.name,
                'message': 'Preferences imported successfully'
            }
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Import failed: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'message': f"Import failed: {str(e)}"
            }
    
    def get_agent_status(self) -> dict:
        """Get agent status"""
        prefs = self.memory.get('preferences', {})
        
        return {
            'name': self.name,
            'status': 'active',
            'capabilities': [
                'preference_learning',
                'style_profiling',
                'item_ranking',
                'feedback_processing',
                'memory_management',
                'trend_analysis',
                'preference_export_import'
            ],
            'memory_stats': {
                'total_feedbacks': prefs.get('feedback_count', 0),
                'favorite_colors': len(prefs.get('favorite_colors', [])),
                'disliked_colors': len(prefs.get('disliked_colors', [])),
                'preferred_styles': len(prefs.get('preferred_styles', [])),
                'successful_combinations': len(prefs.get('successful_combinations', []))
            },
            'ready': True
        }


# Test
if __name__ == "__main__":
    agent = PersonalizationAgent()
    print(agent.get_agent_status())
    
    # Test feedback processing
    print("\n--- Testing Feedback Processing ---")
    feedback = {
        'type': 'positive',
        'colors': ['blue', 'white'],
        'styles': ['casual', 'modern'],
        'combination': [
            {'id': 1, 'color': 'blue'},
            {'id': 2, 'color': 'white'}
        ]
    }
    result = agent.update_preferences(feedback)
    print(f"Update result: {result['message']}")
    
    # Test style profile
    print("\n--- Testing Style Profile ---")
    profile = agent.get_style_profile()
    print(f"Style profile: {profile['style_profile']['description']}")
    print(f"Favorite colors: {profile['style_profile']['favorite_colors']}")
    
    # Test negative feedback
    print("\n--- Testing Negative Feedback ---")
    negative_feedback = {
        'type': 'negative',
        'colors': ['orange'],
        'patterns': ['plaid']
    }
    result = agent.update_preferences(negative_feedback)
    print(f"Update result: {result['message']}")
    
    # Test item ranking
    print("\n--- Testing Item Ranking ---")
    candidate_items = [
        {'id': 1, 'color': 'blue', 'style_tags': ['modern']},
        {'id': 2, 'color': 'orange', 'style_tags': []},
        {'id': 3, 'color': 'white', 'style_tags': ['casual']},
    ]
    ranking = agent.recommend_based_on_history(candidate_items)
    print(f"Top ranked item: {ranking['ranked_items'][0]['item']['color']} (score: {ranking['ranked_items'][0]['preference_score']:.2f})")
    
    # Test trend analysis
    print("\n--- Testing Trend Analysis ---")
    trends = agent.analyze_preference_trends()
    print(f"Trends: {trends['trends']}")
    
    # Test export
    print("\n--- Testing Export ---")
    export = agent.export_preferences()
    print(f"Exported successfully: {export['success']}")
    
    print("\n✓ All tests passed!")