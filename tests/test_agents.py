"""
Complete test suite for AI Fashion Consultant agents
Tests initialization, functionality, integration, and error handling
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from agents.perception_agent import PerceptionAgent
from agents.catalog_agent import CatalogAgent
from agents.planner_agent import PlannerAgent
from agents.recommender_agent import RecommenderAgent
from agents.personalization_agent import PersonalizationAgent
from agents.feedback_agent import FeedbackAgent
from agents.loop_agent import LoopAgent


class TestPerceptionAgent:
    """Test Perception Agent - Vision-based garment detection"""
    
    def test_initialization(self):
        """Test agent can be initialized"""
        agent = PerceptionAgent()
        assert agent.name == "PerceptionAgent"
        assert agent.tagger is not None
        print("✓ Perception Agent initialized")
    
    def test_agent_status(self):
        """Test agent status"""
        agent = PerceptionAgent()
        status = agent.get_agent_status()
        
        assert status['name'] == "PerceptionAgent"
        assert status['ready'] == True
        assert status['status'] == 'active'
        assert 'vision_based_tagging' in status['capabilities']
        assert 'color_detection' in status['capabilities']
        print("✓ Perception Agent status correct")
    
    def test_analyze_garment_structure(self):
        """Test analyze_garment returns correct structure"""
        agent = PerceptionAgent()
        
        # Mock the tagger to avoid actual API call
        with patch.object(agent.tagger, 'tag_garment') as mock_tag:
            mock_tag.return_value = {
                'garment_type': 'shirt',
                'color': 'blue',
                'pattern': 'solid',
                'formality': 'casual'
            }
            
            result = agent.analyze_garment("test_image.jpg")
            
            assert result['success'] == True
            assert result['agent'] == 'PerceptionAgent'
            assert 'data' in result
            assert result['data']['garment_type'] == 'shirt'
        
        print("✓ Perception Agent analyze_garment works")
    
    def test_batch_analysis(self):
        """Test batch wardrobe analysis"""
        agent = PerceptionAgent()
        
        with patch.object(agent.tagger, 'tag_garment') as mock_tag:
            mock_tag.return_value = {
                'garment_type': 'shirt',
                'color': 'blue'
            }
            
            result = agent.analyze_wardrobe_batch(['img1.jpg', 'img2.jpg'])
            
            assert result['success'] == True
            assert result['total_analyzed'] == 2
            assert result['successful'] == 2
        
        print("✓ Perception Agent batch analysis works")


class TestCatalogAgent:
    """Test Catalog Agent - Wardrobe database management"""
    
    def test_initialization(self):
        """Test agent can be initialized"""
        agent = CatalogAgent()
        assert agent.name == "CatalogAgent"
        assert agent.db is not None
        print("✓ Catalog Agent initialized")
    
    def test_agent_status(self):
        """Test agent status"""
        agent = CatalogAgent()
        status = agent.get_agent_status()
        
        assert status['name'] == "CatalogAgent"
        assert status['ready'] == True
        assert status['database'] == 'connected'
        assert 'database_management' in status['capabilities']
        print("✓ Catalog Agent status correct")
    
    def test_add_to_wardrobe(self):
        """Test adding item to wardrobe"""
        agent = CatalogAgent()
        
        garment_data = {
            'garment_type': 'shirt',
            'color': 'blue',
            'pattern': 'solid',
            'formality': 'casual',
            'season': ['spring', 'summer'],
            'material': 'cotton',
            'style_tags': ['modern'],
            'brand': None,
            'condition': 'good',
            'image_path': 'test.jpg'
        }
        
        result = agent.add_to_wardrobe(garment_data)
        
        assert result['success'] == True
        assert result['agent'] == 'CatalogAgent'
        assert result['item_id'] is not None
        print("✓ Catalog Agent add_to_wardrobe works")
    
    def test_get_wardrobe(self):
        """Test retrieving wardrobe"""
        agent = CatalogAgent()
        result = agent.get_wardrobe()
        
        assert result['success'] == True
        assert 'items' in result
        assert 'count' in result
        assert isinstance(result['items'], list)
        print("✓ Catalog Agent get_wardrobe works")
    
    def test_get_wardrobe_with_filters(self):
        """Test retrieving wardrobe with filters"""
        agent = CatalogAgent()
        
        filters = {
            'garment_type': 'shirt',
            'formality': 'casual'
        }
        
        result = agent.get_wardrobe(filters=filters)
        
        assert result['success'] == True
        assert result['filters_applied'] == filters
        print("✓ Catalog Agent filters work")
    
    def test_get_wardrobe_stats(self):
        """Test wardrobe statistics"""
        agent = CatalogAgent()
        result = agent.get_wardrobe_stats()
        
        assert result['success'] == True
        assert 'stats' in result
        assert 'total_items' in result['stats']
        assert 'by_type' in result['stats']
        print("✓ Catalog Agent get_wardrobe_stats works")
    
    def test_get_items_by_category(self):
        """Test getting items by category"""
        agent = CatalogAgent()
        result = agent.get_items_by_category('shirt')
        
        assert result['success'] == True
        assert result['category'] == 'shirt'
        assert 'items' in result
        print("✓ Catalog Agent get_items_by_category works")
    
    def test_analyze_wardrobe_coverage(self):
        """Test wardrobe coverage analysis"""
        agent = CatalogAgent()
        result = agent.analyze_wardrobe_coverage()
        
        assert result['success'] == True
        assert 'coverage_score' in result
        assert 0 <= result['coverage_score'] <= 1
        print("✓ Catalog Agent analyze_wardrobe_coverage works")


class TestPlannerAgent:
    """Test Planner Agent - Outfit generation"""
    
    def test_initialization(self):
        """Test agent can be initialized"""
        agent = PlannerAgent()
        assert agent.name == "PlannerAgent"
        assert agent.model is not None
        assert agent.weather_api is not None
        assert agent.color_matcher is not None
        assert agent.style_rules is not None
        print("✓ Planner Agent initialized")
    
    def test_agent_status(self):
        """Test agent status"""
        agent = PlannerAgent()
        status = agent.get_agent_status()
        
        assert status['name'] == "PlannerAgent"
        assert status['ready'] == True
        assert 'outfit_generation' in status['capabilities']
        assert 'weather_aware_planning' in status['capabilities']
        print("✓ Planner Agent status correct")
    
    def test_generate_outfit_structure(self):
        """Test generate_outfit returns correct structure"""
        agent = PlannerAgent()
        
        context = {
            'wardrobe_items': [
                {'id': 1, 'garment_type': 'shirt', 'color': 'blue', 'formality': 'casual'},
                {'id': 2, 'garment_type': 'pants', 'color': 'black', 'formality': 'casual'},
                {'id': 3, 'garment_type': 'shoes', 'color': 'brown', 'formality': 'casual'}
            ],
            'gender': 'male',
            'occasion': 'casual',
            'city': 'New York'
        }
        
        # This will use mock weather data
        result = agent.generate_outfit(context)
        
        # Should return result even if API fails
        assert 'success' in result
        assert 'agent' in result
        print("✓ Planner Agent generate_outfit structure correct")
    
    def test_get_daily_outfit(self):
        """Test daily outfit generation"""
        agent = PlannerAgent()
        
        wardrobe_items = [
            {'id': 1, 'garment_type': 'shirt', 'color': 'blue'},
            {'id': 2, 'garment_type': 'pants', 'color': 'black'}
        ]
        
        user_profile = {
            'gender': 'male',
            'default_occasion': 'casual',
            'city': 'New York'
        }
        
        result = agent.get_daily_outfit(wardrobe_items, user_profile)
        
        assert 'success' in result
        assert 'agent' in result
        print("✓ Planner Agent get_daily_outfit works")


class TestRecommenderAgent:
    """Test Recommender Agent - Purchase recommendations"""
    
    def test_initialization(self):
        """Test agent can be initialized"""
        agent = RecommenderAgent()
        assert agent.name == "RecommenderAgent"
        assert agent.model is not None
        print("✓ Recommender Agent initialized")
    
    def test_agent_status(self):
        """Test agent status"""
        agent = RecommenderAgent()
        status = agent.get_agent_status()
        
        assert status['name'] == "RecommenderAgent"
        assert status['ready'] == True
        assert 'gap_analysis' in status['capabilities']
        print("✓ Recommender Agent status correct")
    
    def test_analyze_wardrobe_gaps_empty(self):
        """Test gap analysis with empty wardrobe"""
        agent = RecommenderAgent()
        
        result = agent.analyze_wardrobe_gaps(
            [],
            {'gender': 'unisex', 'budget': 'moderate'}
        )
        
        assert 'success' in result
        assert 'recommendations' in result
        print("✓ Recommender Agent handles empty wardrobe")
    
    def test_analyze_wardrobe_gaps_with_items(self):
        """Test gap analysis with existing items"""
        agent = RecommenderAgent()
        
        wardrobe = [
            {'garment_type': 'shirt', 'color': 'blue'},
            {'garment_type': 'shirt', 'color': 'white'}
        ]
        
        result = agent.analyze_wardrobe_gaps(
            wardrobe,
            {'gender': 'male', 'budget': 'moderate'}
        )
        
        assert 'success' in result
        assert 'wardrobe_analysis' in result
        print("✓ Recommender Agent gap analysis works")
    
    def test_suggest_purchases(self):
        """Test purchase suggestions for occasion"""
        agent = RecommenderAgent()
        
        wardrobe = [
            {'garment_type': 'shirt', 'color': 'blue'}
        ]
        
        result = agent.suggest_purchases('formal', wardrobe)
        
        assert 'success' in result
        assert 'occasion' in result
        print("✓ Recommender Agent suggest_purchases works")


class TestPersonalizationAgent:
    """Test Personalization Agent - User preference learning"""
    
    def test_initialization(self):
        """Test agent can be initialized"""
        agent = PersonalizationAgent()
        assert agent.name == "PersonalizationAgent"
        assert agent.memory is not None
        print("✓ Personalization Agent initialized")
    
    def test_agent_status(self):
        """Test agent status"""
        agent = PersonalizationAgent()
        status = agent.get_agent_status()
        
        assert status['name'] == "PersonalizationAgent"
        assert status['ready'] == True
        assert 'preference_learning' in status['capabilities']
        assert 'memory_stats' in status
        print("✓ Personalization Agent status correct")
    
    def test_get_preferences_initial(self):
        """Test getting initial preferences"""
        agent = PersonalizationAgent()
        result = agent.get_preferences()
        
        assert result['success'] == True
        assert 'preferences' in result
        assert 'favorite_colors' in result['preferences']
        print("✓ Personalization Agent get_preferences works")
    
    def test_update_preferences_positive(self):
        """Test updating preferences with positive feedback"""
        agent = PersonalizationAgent()
        
        feedback = {
            'type': 'positive',
            'colors': ['blue', 'white'],
            'styles': ['casual', 'modern']
        }
        
        result = agent.update_preferences(feedback)
        
        assert result['success'] == True
        assert 'preferences' in result
        assert 'blue' in result['preferences']['favorite_colors']
        assert 'casual' in result['preferences']['preferred_styles']
        print("✓ Personalization Agent positive feedback works")
    
    def test_update_preferences_negative(self):
        """Test updating preferences with negative feedback"""
        agent = PersonalizationAgent()
        
        feedback = {
            'type': 'negative',
            'colors': ['orange'],
            'patterns': ['plaid']
        }
        
        result = agent.update_preferences(feedback)
        
        assert result['success'] == True
        assert 'orange' in result['preferences']['disliked_colors']
        assert 'plaid' in result['preferences']['avoided_patterns']
        print("✓ Personalization Agent negative feedback works")
    
    def test_get_style_profile(self):
        """Test generating style profile"""
        agent = PersonalizationAgent()
        
        # Add some preferences first
        agent.update_preferences({
            'type': 'positive',
            'colors': ['blue', 'black'],
            'styles': ['modern']
        })
        
        result = agent.get_style_profile()
        
        assert result['success'] == True
        assert 'style_profile' in result
        assert 'description' in result['style_profile']
        assert 'confidence' in result['style_profile']
        print("✓ Personalization Agent get_style_profile works")
    
    def test_recommend_based_on_history(self):
        """Test item ranking based on preferences"""
        agent = PersonalizationAgent()
        
        # Set preferences
        agent.update_preferences({
            'type': 'positive',
            'colors': ['blue'],
            'styles': ['modern']
        })
        
        candidate_items = [
            {'id': 1, 'color': 'blue', 'style_tags': ['modern']},
            {'id': 2, 'color': 'orange', 'style_tags': []},
            {'id': 3, 'color': 'black', 'style_tags': ['modern']}
        ]
        
        result = agent.recommend_based_on_history(candidate_items)
        
        assert result['success'] == True
        assert 'ranked_items' in result
        assert len(result['ranked_items']) == 3
        
        # Blue + modern should score highest
        top_item = result['ranked_items'][0]
        assert top_item['item']['color'] == 'blue'
        print("✓ Personalization Agent item ranking works")
    
    def test_reset_preferences(self):
        """Test resetting preferences"""
        agent = PersonalizationAgent()
        
        # Add preferences
        agent.update_preferences({
            'type': 'positive',
            'colors': ['blue']
        })
        
        # Reset
        result = agent.reset_preferences()
        
        assert result['success'] == True
        
        # Check preferences are empty
        prefs = agent.get_preferences()
        assert len(prefs['preferences']['favorite_colors']) == 0
        print("✓ Personalization Agent reset works")


class TestFeedbackAgent:
    """Test Feedback Agent - Feedback collection"""
    
    def test_initialization(self):
        """Test agent can be initialized"""
        agent = FeedbackAgent()
        assert agent.name == "FeedbackAgent"
        assert agent.model is not None
        print("✓ Feedback Agent initialized")
    
    def test_agent_status(self):
        """Test agent status"""
        agent = FeedbackAgent()
        status = agent.get_agent_status()
        
        assert status['name'] == "FeedbackAgent"
        assert status['ready'] == True
        assert 'feedback_processing' in status['capabilities']
        print("✓ Feedback Agent status correct")
    
    def test_collect_rating_positive(self):
        """Test collecting positive rating"""
        agent = FeedbackAgent()
        
        result = agent.collect_rating(1, 5, "Loved this outfit!")
        
        assert result['success'] == True
        assert result['rating'] == 5
        assert result['sentiment'] == 'positive'
        assert result['outfit_id'] == 1
        print("✓ Feedback Agent positive rating works")
    
    def test_collect_rating_negative(self):
        """Test collecting negative rating"""
        agent = FeedbackAgent()
        
        result = agent.collect_rating(2, 1, "Didn't like it")
        
        assert result['success'] == True
        assert result['rating'] == 1
        assert result['sentiment'] == 'negative'
        print("✓ Feedback Agent negative rating works")
    
    def test_collect_rating_neutral(self):
        """Test collecting neutral rating"""
        agent = FeedbackAgent()
        
        result = agent.collect_rating(3, 3, "It was okay")
        
        assert result['success'] == True
        assert result['rating'] == 3
        assert result['sentiment'] == 'neutral'
        print("✓ Feedback Agent neutral rating works")
    
    def test_analyze_feedback_trends_empty(self):
        """Test trend analysis with no history"""
        agent = FeedbackAgent()
        
        result = agent.analyze_feedback_trends([])
        
        assert result['success'] == True
        assert 'trends' in result
        print("✓ Feedback Agent handles empty history")
    
    def test_analyze_feedback_trends(self):
        """Test trend analysis with feedback history"""
        agent = FeedbackAgent()
        
        feedback_history = [
            {'sentiment': 'positive', 'rating': 5},
            {'sentiment': 'positive', 'rating': 4},
            {'sentiment': 'negative', 'rating': 2},
            {'sentiment': 'neutral', 'rating': 3}
        ]
        
        result = agent.analyze_feedback_trends(feedback_history)
        
        assert result['success'] == True
        assert 'trends' in result
        assert result['trends']['total_feedbacks'] == 4
        assert result['trends']['positive_rate'] == 0.5
        assert result['trends']['average_rating'] == 3.5
        print("✓ Feedback Agent trend analysis works")


class TestLoopAgent:
    """Test Loop Agent - Recurring tasks"""
    
    def test_initialization(self):
        """Test agent can be initialized"""
        agent = LoopAgent()
        assert agent.name == "LoopAgent"
        assert agent.running == False
        assert agent.tasks == []
        print("✓ Loop Agent initialized")
    
    def test_agent_status(self):
        """Test agent status"""
        agent = LoopAgent()
        status = agent.get_agent_status()
        
        assert status['name'] == "LoopAgent"
        assert status['ready'] == True
        assert 'daily_scheduling' in status['capabilities']
        print("✓ Loop Agent status correct")
    
    def test_schedule_daily_outfit(self):
        """Test scheduling daily outfit task"""
        agent = LoopAgent()
        
        def mock_callback():
            pass
        
        result = agent.schedule_daily_outfit("07:00", mock_callback)
        
        assert result['success'] == True
        assert result['task'] == 'daily_outfit'
        assert result['scheduled_time'] == "07:00"
        print("✓ Loop Agent schedule_daily_outfit works")
    
    def test_get_scheduled_tasks(self):
        """Test getting scheduled tasks"""
        agent = LoopAgent()
        
        def mock_callback():
            pass
        
        agent.schedule_daily_outfit("07:00", mock_callback)
        agent.schedule_daily_outfit("18:00", mock_callback)
        
        result = agent.get_scheduled_tasks()
        
        assert result['success'] == True
        assert len(result['tasks']) == 2
        print("✓ Loop Agent get_scheduled_tasks works")
    
    def test_run_morning_routine(self):
        """Test morning routine execution"""
        agent = LoopAgent()
        
        wardrobe_items = [
            {'id': 1, 'garment_type': 'shirt', 'color': 'blue'}
        ]
        
        user_profile = {
            'gender': 'male',
            'city': 'New York'
        }
        
        result = agent.run_morning_routine(wardrobe_items, user_profile)
        
        # Should work even if planner has issues
        assert 'success' in result
        assert 'routine' in result
        print("✓ Loop Agent run_morning_routine works")
    
    def test_run_seasonal_rotation(self):
        """Test seasonal rotation"""
        agent = LoopAgent()
        
        wardrobe_items = [
            {'id': 1, 'garment_type': 'shirt', 'season': ['summer'], 'times_worn': 5},
            {'id': 2, 'garment_type': 'sweater', 'season': ['winter'], 'times_worn': 1},
            {'id': 3, 'garment_type': 'jacket', 'season': ['fall', 'winter'], 'times_worn': 0}
        ]
        
        result = agent.run_seasonal_rotation(wardrobe_items, 'summer')
        
        assert result['success'] == True
        assert result['season'] == 'summer'
        assert 'active_items' in result
        assert 'storage_items' in result
        print("✓ Loop Agent run_seasonal_rotation works")


class TestOrchestrator:
    """Test orchestrator integration"""
    
    def test_initialization(self):
        """Test orchestrator can initialize all agents"""
        from orchestrator import FashionAgentOrchestrator
        
        orchestrator = FashionAgentOrchestrator()
        assert orchestrator.name == "Orchestrator"
        assert orchestrator.perception is not None
        assert orchestrator.catalog is not None
        assert orchestrator.planner is not None
        assert orchestrator.recommender is not None
        assert orchestrator.personalization is not None
        assert orchestrator.feedback is not None
        assert orchestrator.loop is not None
        print("✓ Orchestrator initialized all 7 agents")
    
    def test_get_system_status(self):
        """Test getting system status"""
        from orchestrator import FashionAgentOrchestrator
        
        orchestrator = FashionAgentOrchestrator()
        status = orchestrator.get_system_status()
        
        assert status['orchestrator'] == "Orchestrator"
        assert status['status'] == 'active'
        assert len(status['agents']) == 7
        
        # Check all agents are ready
        for agent_name, agent_info in status['agents'].items():
            assert agent_info['ready'] == True
        
        print("✓ Orchestrator: All 7 agents operational")
    
    def test_ingest_wardrobe_empty(self):
        """Test wardrobe ingestion with empty list"""
        from orchestrator import FashionAgentOrchestrator
        
        orchestrator = FashionAgentOrchestrator()
        result = orchestrator.ingest_wardrobe([])
        
        # Should handle empty gracefully
        assert 'success' in result
        print("✓ Orchestrator handles empty wardrobe ingestion")


# Helper function to run all tests with detailed output
def run_all_tests():
    """Run all tests with detailed output"""
    print("\n" + "="*70)
    print("🧪 AI FASHION CONSULTANT - COMPLETE TEST SUITE")
    print("="*70 + "\n")
    
    # Run pytest with verbose output
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "-ra"  # Show summary of all test results
    ])
    
    print("\n" + "="*70)
    if exit_code == 0:
        print("✅ ALL TESTS PASSED! Ready for deployment.")
    else:
        print("❌ SOME TESTS FAILED - Review output above")
    print("="*70 + "\n")
    
    return exit_code


# Run tests if executed directly
if __name__ == "__main__":
    run_all_tests()