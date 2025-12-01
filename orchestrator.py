"""Main orchestrator - coordinates all agents"""

import logging
import time
from datetime import datetime
from typing import Dict, List
from agents.perception_agent import PerceptionAgent
from agents.catalog_agent import CatalogAgent
from agents.planner_agent import PlannerAgent
from agents.recommender_agent import RecommenderAgent
from agents.personalization_agent import PersonalizationAgent
from agents.feedback_agent import FeedbackAgent
from agents.loop_agent import LoopAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FashionAgentOrchestrator:
    """
    Main orchestrator implementing a Hub-and-Spoke architecture.
    
    ARCHITECTURE DESIGN DECISIONS:
    1. Centralized State Management: The Orchestrator holds the 'Session Context' 
       (user profile, weather, current inventory), preventing state drift between agents.
    2. Agent Specialization: 
       - Perception: Computer Vision tasks (CPU/GPU heavy).
       - Planner: Reasoning and LLM generation (API latency bound).
       - Catalog: I/O operations (Disk bound).
       Separating these allows for independent scaling and error isolation.
    3. Fail-Safe Orchestration: If the 'Planner' (LLM) fails due to API limits,
       the Orchestrator can fallback to procedural logic without crashing the app.
    """
    
    def __init__(self):
        self.name = "Orchestrator"
        self.start_time = time.time()
        self.activity_log = []  # Store actions for the UI
        
        # Initialize all agents 
        self._log_activity("System", "Initializing multi-agent swarm...")
        self.perception = PerceptionAgent()
        self.catalog = CatalogAgent()
        self.planner = PlannerAgent()
        self.recommender = RecommenderAgent()
        self.personalization = PersonalizationAgent()
        self.feedback = FeedbackAgent()
        self.loop = LoopAgent()
        
        self._log_activity("System", "All 7 agents initialized and ready.")
        logger.info(f"✓ {self.name} initialized with 7 agents")
    
    def _log_activity(self, source: str, message: str):
        """Internal logger for UI display"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.activity_log.insert(0, {  # Prepend to show newest first
            "time": timestamp,
            "source": source,
            "message": message
        })
        # Keep log size manageable
        if len(self.activity_log) > 50:
            self.activity_log.pop()

    def ingest_wardrobe(self, image_paths: List[str]) -> Dict:
        """Complete wardrobe ingestion pipeline"""
        self._log_activity("Orchestrator", f"Starting ingestion pipeline for {len(image_paths)} images")
        
        start = time.time()
        # Step 1: Perception (Vision Analysis)
        perception_result = self.perception.analyze_wardrobe_batch(image_paths)
        
        if not perception_result['success']:
            self._log_activity("PerceptionAgent", "❌ Vision analysis failed")
            return {'success': False, 'message': 'Failed to analyze images'}
        
        self._log_activity("PerceptionAgent", f"Analyzed {len(image_paths)} images via Gemini Vision")
        
        # Step 2: Catalog (Persistence)
        stored_items = []
        for result in perception_result['results']:
            if result['success']:
                catalog_result = self.catalog.add_to_wardrobe(result['data'])
                if catalog_result['success']:
                    stored_items.append(catalog_result['item_id'])
        
        duration = round(time.time() - start, 2)
        self._log_activity("CatalogAgent", f"Indexed {len(stored_items)} items in vector DB ({duration}s)")
        
        stats = self.catalog.get_wardrobe_stats()
        
        return {
            'success': True,
            'orchestrator': self.name,
            'images_processed': len(image_paths),
            'items_stored': len(stored_items),
            'wardrobe_stats': stats['stats'],
            'message': f"Ingested {len(stored_items)}/{len(image_paths)} items successfully"
        }
    
    def generate_daily_outfit(self, user_profile: Dict) -> Dict:
        """
        Generate daily outfit recommendation with history awareness.
        Implements the 'Retrieve-Then-Reason' pattern.
        """
        self._log_activity("Orchestrator", "Triggering daily outfit workflow")
        start = time.time()
        
        # Step 1: Retrieval (Wardrobe Inventory)
        wardrobe_result = self.catalog.get_wardrobe()
        if not wardrobe_result['success'] or not wardrobe_result['items']:
            return {'success': False, 'message': 'No wardrobe items available'}
        
        # Step 2: Context Augmentation (User Prefs & History)
        prefs_result = self.personalization.get_preferences()
        preferences = prefs_result.get('preferences', {})
        self._log_activity("PersonalizationAgent", "Retrieved user style graph")
        
        recent_result = self.catalog.get_recent_outfits(limit=5)
        recent_outfits = recent_result.get('outfits', [])

        # Get outfits worn today to enforce variety constraints
        worn_result = self.catalog.get_outfits_worn_today()
        worn_today = worn_result.get('outfits', [])
        
        # Step 3: Context Assembly
        context = {
            'wardrobe_items': wardrobe_result['items'],
            'gender': user_profile.get('gender', 'unisex'),
            'occasion': user_profile.get('occasion', 'casual'),
            'city': user_profile.get('city', 'New York'),
            'preferences': preferences.get('favorite_colors', []),
            'dislikes': preferences.get('disliked_colors', []),
            'recent_outfits': recent_outfits,
            'worn_today': worn_today
        }
        
        # Step 4: Reasoning (The "Brain")
        self._log_activity("PlannerAgent", "Reasoning on outfit combinations...")
        outfit_result = self.planner.generate_outfit(context)
        
        if not outfit_result['success']:
            return {'success': False, 'message': 'Failed to generate outfit'}
            
        # Step 5: Persistence (Save State)
        save_result = self.catalog.save_generated_outfit(
            outfit_result['outfit'], 
            {
                'occasion': context['occasion'],
                'weather': str(outfit_result['weather']),
                'temperature': outfit_result['weather'].get('temperature'),
                'gender': context['gender']
            }
        )
        outfit_id = save_result.get('outfit_id')
        
        duration = round(time.time() - start, 2)
        self._log_activity("Orchestrator", f"Outfit generated and cached (ID: {outfit_id}) in {duration}s")
        
        return {
            'success': True,
            'orchestrator': self.name,
            'outfit': outfit_result['outfit'],
            'outfit_id': outfit_id, 
            'reasoning': outfit_result['reasoning'],
            'confidence_score': outfit_result['confidence_score'],
            'color_analysis': outfit_result['color_analysis'],
            'weather': outfit_result['weather'],
            'styling_tips': outfit_result['styling_tips'],
            'alternatives': outfit_result.get('alternatives', []),
            'message': 'Daily outfit generated successfully'
        }
    
    def confirm_outfit_choice(self, outfit_id: int) -> Dict:
        """User confirms they are wearing this outfit today"""
        result = self.catalog.mark_outfit_worn(outfit_id)
        self._log_activity("CatalogAgent", f"Marked outfit #{outfit_id} as worn today")
        return result

    def delete_wardrobe_item(self, item_id: int) -> Dict:
        """Delete an item from the wardrobe"""
        result = self.catalog.delete_item(item_id)
        self._log_activity("CatalogAgent", f"Deleted item #{item_id}")
        return result
    
    def process_outfit_feedback(self, outfit_id: int, feedback_text: str, rating: int) -> Dict:
        """
        Process user feedback Loop.
        Feeds sentiment back into the PersonalizationAgent to update Long-Term Memory.
        """
        self._log_activity("FeedbackAgent", f"Analyzing sentiment for outfit #{outfit_id}")
        feedback_result = self.feedback.process_feedback(feedback_text, {'outfit_id': outfit_id}, {'outfit_id': outfit_id})
        
        self._log_activity("FeedbackAgent", "Recording structured rating")
        rating_result = self.feedback.collect_rating(outfit_id, rating, feedback_text)
        
        personalization_result = {}
        if feedback_result['success']:
            insights = feedback_result.get('insights', {})
            pref_update = {
                'type': feedback_result['sentiment'],
                'colors': insights.get('specific_elements', {}).get('colors', []),
                'styles': insights.get('specific_elements', {}).get('styles', [])
            }
            self._log_activity("PersonalizationAgent", "Updating user long-term memory")
            personalization_result = self.personalization.update_preferences(pref_update)
        
        return {
            'success': True,
            'feedback_processed': feedback_result['success'],
            'preferences_updated': personalization_result.get('success', False),
            'sentiment': feedback_result.get('sentiment'),
            'message': 'Feedback processed'
        }
    
    def get_purchase_recommendations(self, user_profile: Dict) -> Dict:
        """Get smart purchase recommendations"""
        self._log_activity("RecommenderAgent", "Starting wardrobe gap analysis")
        wardrobe_result = self.catalog.get_wardrobe()
        if not wardrobe_result['success']:
             return {'success': False, 'message': 'Could not access wardrobe'}
        
        prefs_result = self.personalization.get_preferences()
        full_profile = {
            **user_profile,
            'favorite_colors': prefs_result.get('preferences', {}).get('favorite_colors', []),
            'preferred_styles': prefs_result.get('preferences', {}).get('preferred_styles', [])
        }
        
        recommendations_result = self.recommender.analyze_wardrobe_gaps(wardrobe_result['items'], full_profile)
        self._log_activity("RecommenderAgent", f"Generated {len(recommendations_result.get('recommendations', []))} purchase ideas")
        
        if not recommendations_result['success']:
            return {'success': False, 'message': 'Failed to generate recommendations'}

        return {
            'success': True,
            'recommendations': recommendations_result['recommendations'],
            'wardrobe_analysis': recommendations_result['wardrobe_analysis'],
            'message': f"Found {len(recommendations_result['recommendations'])} recommendations"
        }
    
    def run_seasonal_rotation(self, season: str) -> Dict:
        """Execute seasonal wardrobe rotation"""
        wardrobe_result = self.catalog.get_wardrobe()
        if not wardrobe_result['success']:
            return {'success': False, 'message': 'Could not access wardrobe'}
        self._log_activity("LoopAgent", f"Executing seasonal rotation for {season}")
        return self.loop.run_seasonal_rotation(wardrobe_result['items'], season)
    
    def get_system_status(self) -> Dict:
        """Get status of all agents"""
        uptime = round(time.time() - self.start_time)
        
        return {
            'orchestrator': self.name,
            'status': 'active',
            'uptime_seconds': uptime,
            'agents': {
                'perception': self.perception.get_agent_status(),
                'catalog': self.catalog.get_agent_status(),
                'planner': self.planner.get_agent_status(),
                'recommender': self.recommender.get_agent_status(),
                'personalization': self.personalization.get_agent_status(),
                'feedback': self.feedback.get_agent_status(),
                'loop': self.loop.get_agent_status()
            },
            'recent_activity': self.activity_log,
            'message': 'All systems operational'
        }

if __name__ == "__main__":
    orchestrator = FashionAgentOrchestrator()
    print(f"System status: {orchestrator.get_system_status()['status']}")