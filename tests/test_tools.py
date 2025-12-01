"""
Complete test suite for AI Fashion Consultant tools
Tests all custom tools and integrations
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import json
import os
import time

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from tools.image_tagger import ImageTagger
from tools.wardrobe_db import WardrobeDB
from tools.weather_api import WeatherAPI
from tools.color_matcher import ColorMatcher
from tools.gender_style_rules import GenderStyleRules
from tools.calendar_reader import CalendarReader
from memory.memory_manager import MemoryManager
from memory.session_service import SessionService


# ============================================================================
# TEST IMAGE TAGGER
# ============================================================================

class TestImageTagger:
    """Test Image Tagger Tool"""
    
    def test_initialization(self):
        """Test tool can be initialized"""
        tagger = ImageTagger()
        assert tagger.model is not None
        print("✓ ImageTagger initialized")
    
    def test_fallback_tags(self):
        """Test fallback tags generation"""
        tagger = ImageTagger()
        tags = tagger._fallback_tags("test.jpg", "Test error")
        
        assert tags['garment_type'] == 'unknown'
        assert tags['color'] == 'unknown'
        assert tags['tagged_by'] == 'fallback'
        assert tags['image_path'] == 'test.jpg'
        assert 'error' in tags
        print("✓ ImageTagger fallback tags work")
    
    def test_tag_garment_structure(self):
        """Test tag_garment returns correct structure"""
        tagger = ImageTagger()
        tags = tagger.tag_garment("nonexistent.jpg")
        
        assert 'garment_type' in tags
        assert 'color' in tags
        assert 'formality' in tags
        assert 'season' in tags
        assert 'pattern' in tags
        print("✓ ImageTagger returns correct structure")
    
    def test_batch_tag(self):
        """Test batch tagging"""
        tagger = ImageTagger()
        results = tagger.batch_tag(["img1.jpg", "img2.jpg"])
        
        assert len(results) == 2
        assert all('garment_type' in r for r in results)
        print("✓ ImageTagger batch_tag works")


# ============================================================================
# TEST WARDROBE DATABASE
# ============================================================================

class TestWardrobeDB:
    """Test Wardrobe Database"""
    
    @pytest.fixture
    def test_db(self):
        """Create a test database"""
        test_db_path = "data/test_wardrobe_temp.db"
        db = WardrobeDB(test_db_path)
        yield db
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
    
    def test_initialization(self, test_db):
        """Test database initialization"""
        assert test_db.db_path == "data/test_wardrobe_temp.db"
        print("✓ WardrobeDB initialized")
    
    def test_add_item(self, test_db):
        """Test adding item to database"""
        tags = {
            'garment_type': 'shirt',
            'color': 'blue',
            'secondary_colors': ['white'],
            'pattern': 'solid',
            'formality': 'casual',
            'season': ['spring', 'summer'],
            'material': 'cotton',
            'style_tags': ['modern'],
            'brand': None,
            'condition': 'good',
            'image_path': 'test.jpg'
        }
        
        item_id = test_db.add_item(tags)
        assert item_id > 0
        print("✓ WardrobeDB add_item works")
    
    def test_get_all_items(self, test_db):
        """Test retrieving all items"""
        tags = {
            'garment_type': 'shirt',
            'color': 'blue',
            'pattern': 'solid',
            'formality': 'casual',
            'season': ['spring'],
            'material': 'cotton',
            'style_tags': [],
            'brand': None,
            'condition': 'good',
            'image_path': 'test.jpg'
        }
        test_db.add_item(tags)
        
        items = test_db.get_all_items()
        assert len(items) > 0
        assert items[0]['garment_type'] == 'shirt'
        print("✓ WardrobeDB get_all_items works")
    
    def test_get_items_by_type(self, test_db):
        """Test getting items by type"""
        tags1 = {
            'garment_type': 'shirt',
            'color': 'blue',
            'pattern': 'solid',
            'formality': 'casual',
            'season': [],
            'material': 'cotton',
            'style_tags': [],
            'brand': None,
            'condition': 'good',
            'image_path': 'test1.jpg'
        }
        tags2 = {
            'garment_type': 'pants',
            'color': 'black',
            'pattern': 'solid',
            'formality': 'casual',
            'season': [],
            'material': 'denim',
            'style_tags': [],
            'brand': None,
            'condition': 'good',
            'image_path': 'test2.jpg'
        }
        
        test_db.add_item(tags1)
        test_db.add_item(tags2)
        shirts = test_db.get_items_by_type('shirt')
        
        assert len(shirts) >= 1
        assert all(item['garment_type'] == 'shirt' for item in shirts)
        print("✓ WardrobeDB get_items_by_type works")
    
    def test_save_outfit(self, test_db):
        """Test saving outfit"""
        outfit = {
            'top': 'Blue Shirt',
            'bottom': 'Black Pants',
            'shoes': 'Brown Shoes'
        }
        metadata = {
            'occasion': 'casual',
            'weather': 'sunny',
            'temperature': 72,
            'gender': 'male'
        }
        
        outfit_id = test_db.save_outfit(outfit, metadata)
        assert outfit_id > 0
        print("✓ WardrobeDB save_outfit works")
    
    def test_save_feedback(self, test_db):
        """Test saving feedback"""
        outfit = {'top': 'shirt'}
        metadata = {'occasion': 'casual'}
        outfit_id = test_db.save_outfit(outfit, metadata)
        
        feedback = {
            'feedback_text': 'Great outfit!',
            'rating': 5
        }
        test_db.save_feedback(outfit_id, feedback)
        print("✓ WardrobeDB save_feedback works")
    
    def test_get_user_preferences(self, test_db):
        """Test getting user preferences"""
        prefs = test_db.get_user_preferences()
        assert 'gender' in prefs
        assert 'favorite_colors' in prefs
        print("✓ WardrobeDB get_user_preferences works")
    
    def test_update_preferences(self, test_db):
        """Test updating preferences"""
        preferences = {
            'gender': 'male',
            'favorite_colors': ['blue', 'black'],
            'disliked_colors': ['orange'],
            'preferred_styles': ['modern'],
            'sizes': {'shirt': 'M', 'pants': '32'}
        }
        test_db.update_preferences(preferences)
        
        saved_prefs = test_db.get_user_preferences()
        assert saved_prefs['gender'] == 'male'
        print("✓ WardrobeDB update_preferences works")
    
    def test_get_wardrobe_stats(self, test_db):
        """Test getting wardrobe statistics"""
        for i in range(3):
            tags = {
                'garment_type': 'shirt',
                'color': 'blue',
                'pattern': 'solid',
                'formality': 'casual',
                'season': [],
                'material': 'cotton',
                'style_tags': [],
                'brand': None,
                'condition': 'good',
                'image_path': f'test{i}.jpg'
            }
            test_db.add_item(tags)
        
        stats = test_db.get_wardrobe_stats()
        assert stats['total_items'] >= 3
        assert 'by_type' in stats
        assert 'average_times_worn' in stats
        print("✓ WardrobeDB get_wardrobe_stats works")


# ============================================================================
# TEST WEATHER API
# ============================================================================

class TestWeatherAPI:
    """Test Weather API"""
    
    def test_initialization(self):
        """Test API initialization"""
        api = WeatherAPI()
        assert api.base_url is not None
        print("✓ WeatherAPI initialized")
    
    def test_get_weather_mock(self):
        """Test getting mock weather data"""
        api = WeatherAPI(api_key="mock_key")
        weather = api.get_weather("New York")
        
        assert 'temperature' in weather
        assert 'condition' in weather
        assert 'description' in weather
        assert 'humidity' in weather
        print("✓ WeatherAPI get_weather works")
    
    def test_mock_weather_structure(self):
        """Test mock weather structure"""
        api = WeatherAPI()
        weather = api._mock_weather()
        
        assert weather['temperature'] == 72
        assert weather['condition'] == 'Clear'
        assert weather['city'] == 'Demo City'
        print("✓ WeatherAPI mock weather structure correct")
    
    def test_get_outfit_suggestion_cold(self):
        """Test cold weather suggestion"""
        api = WeatherAPI()
        weather = {'temperature': 30, 'condition': 'Snow'}
        suggestion = api.get_outfit_suggestion(weather)
        assert suggestion == 'cold_weather_heavy'
        print("✓ WeatherAPI cold weather suggestion")
    
    def test_get_outfit_suggestion_mild(self):
        """Test mild weather suggestion"""
        api = WeatherAPI()
        weather = {'temperature': 70, 'condition': 'Partly Cloudy'}
        suggestion = api.get_outfit_suggestion(weather)
        assert suggestion == 'mild_weather_comfortable'
        print("✓ WeatherAPI mild weather suggestion")
    
    def test_get_outfit_suggestion_hot(self):
        """Test hot weather suggestion"""
        api = WeatherAPI()
        weather = {'temperature': 90, 'condition': 'Sunny'}
        suggestion = api.get_outfit_suggestion(weather)
        assert suggestion == 'hot_weather_minimal'
        print("✓ WeatherAPI hot weather suggestion")


# ============================================================================
# TEST COLOR MATCHER
# ============================================================================

class TestColorMatcher:
    """Test Color Matcher"""
    
    def test_initialization(self):
        """Test matcher initialization"""
        matcher = ColorMatcher()
        assert matcher.complementary is not None
        print("✓ ColorMatcher initialized")
    
    def test_validate_combination_good(self):
        """Test good color combination"""
        matcher = ColorMatcher()
        result = matcher.validate_combination(['blue', 'white'])
        assert result['valid'] == True
        assert result['score'] > 0.8
        print("✓ ColorMatcher validates good combinations")
    
    def test_validate_combination_neutral(self):
        """Test neutral colors"""
        matcher = ColorMatcher()
        result = matcher.validate_combination(['black', 'white', 'gray'])
        assert result['valid'] == True
        print("✓ ColorMatcher handles neutrals")
    
    def test_validate_combination_single(self):
        """Test single color"""
        matcher = ColorMatcher()
        result = matcher.validate_combination(['blue'])
        assert result['valid'] == True
        assert result['score'] == 1.0
        print("✓ ColorMatcher handles single color")
    
    def test_suggest_matching_colors(self):
        """Test color suggestions"""
        matcher = ColorMatcher()
        suggestions = matcher.suggest_matching_colors('blue')
        assert len(suggestions) > 0
        print("✓ ColorMatcher suggests colors")
    
    def test_analyze_outfit_colors(self):
        """Test outfit color analysis"""
        matcher = ColorMatcher()
        outfit_items = [
            {'color': 'blue'},
            {'color': 'white'},
            {'color': 'black'}
        ]
        analysis = matcher.analyze_outfit_colors(outfit_items)
        assert 'colors_used' in analysis
        assert 'validation' in analysis
        assert analysis['has_neutral'] == True
        print("✓ ColorMatcher analyzes outfit colors")


# ============================================================================
# TEST GENDER STYLE RULES
# ============================================================================

class TestGenderStyleRules:
    """Test Gender Style Rules"""
    
    def test_initialization(self):
        """Test rules initialization"""
        rules = GenderStyleRules()
        assert 'male' in rules.rules
        assert 'female' in rules.rules
        assert 'unisex' in rules.rules
        print("✓ GenderStyleRules initialized")
    
    def test_get_outfit_requirements(self):
        """Test outfit requirements"""
        rules = GenderStyleRules()
        reqs = rules.get_outfit_requirements('male', 'casual')
        assert 'required_categories' in reqs
        assert reqs['occasion'] == 'casual'
        assert reqs['gender'] == 'male'
        print("✓ GenderStyleRules requirements work")
    
    def test_validate_outfit_complete(self):
        """Test complete outfit validation"""
        rules = GenderStyleRules()
        outfit = {
            'top': 'shirt',
            'bottom': 'pants',
            'shoes': 'shoes'
        }
        result = rules.validate_outfit(outfit, 'male')
        assert result['valid'] == True
        assert result['score'] == 1.0
        print("✓ GenderStyleRules validates complete outfit")
    
    def test_validate_outfit_incomplete(self):
        """Test incomplete outfit"""
        rules = GenderStyleRules()
        outfit = {'top': 'shirt'}
        result = rules.validate_outfit(outfit, 'male')
        assert result['valid'] == False
        assert len(result['missing']) > 0
        print("✓ GenderStyleRules detects missing items")
    
    def test_validate_outfit_too_many_accessories(self):
        """Test accessory limit"""
        rules = GenderStyleRules()
        outfit = {
            'top': 'shirt',
            'bottom': 'pants',
            'shoes': 'shoes',
            'accessories': ['watch', 'belt', 'tie', 'ring', 'bracelet', 'necklace']
        }
        result = rules.validate_outfit(outfit, 'male')
        assert result['valid'] == False
        print("✓ GenderStyleRules enforces accessory limits")
    
    def test_get_styling_tips(self):
        """Test styling tips"""
        rules = GenderStyleRules()
        tips = rules.get_styling_tips('male', 'casual')
        assert len(tips) > 0
        assert all(isinstance(tip, str) for tip in tips)
        print("✓ GenderStyleRules provides tips")


# ============================================================================
# TEST CALENDAR READER
# ============================================================================

class TestCalendarReader:
    """Test Calendar Reader"""
    
    def test_initialization(self):
        """Test calendar initialization"""
        reader = CalendarReader()
        assert reader.name == "CalendarReader"
        print("✓ CalendarReader initialized")
    
    def test_get_todays_events(self):
        """Test getting today's events"""
        reader = CalendarReader()
        result = reader.get_todays_events()
        assert result['success'] == True
        assert 'events' in result
        assert 'occasion' in result
        print("✓ CalendarReader get_todays_events works")
    
    def test_get_upcoming_events(self):
        """Test upcoming events"""
        reader = CalendarReader()
        result = reader.get_upcoming_events(days=7)
        assert result['success'] == True
        assert 'events' in result
        print("✓ CalendarReader get_upcoming_events works")
    
    def test_determine_occasion(self):
        """Test occasion determination"""
        reader = CalendarReader()
        events = [
            {'formality': 'formal', 'type': 'work'},
            {'formality': 'casual', 'type': 'social'}
        ]
        occasion = reader._determine_occasion(events)
        assert occasion == 'formal'
        print("✓ CalendarReader determines occasion")
    
    def test_search_events(self):
        """Test event search"""
        reader = CalendarReader()
        result = reader.search_events('meeting', days=30)
        assert result['success'] == True
        assert 'matches' in result
        print("✓ CalendarReader search_events works")


# ============================================================================
# TEST MEMORY MANAGER
# ============================================================================

class TestMemoryManager:
    """Test Memory Manager"""
    
    @pytest.fixture
    def test_memory(self):
        """Create test memory"""
        test_path = "data/test_memory_temp.json"
        manager = MemoryManager(test_path)
        yield manager
        if os.path.exists(test_path):
            os.remove(test_path)
    
    def test_initialization(self, test_memory):
        """Test memory initialization"""
        assert test_memory.name == "MemoryManager"
        assert test_memory.memory is not None
        print("✓ MemoryManager initialized")
    
    def test_store_and_retrieve(self, test_memory):
        """Test store/retrieve"""
        test_memory.store('test_key', 'test_value', 'test_namespace')
        result = test_memory.retrieve('test_key', 'test_namespace')
        assert result['success'] == True
        assert result['value'] == 'test_value'
        print("✓ MemoryManager store/retrieve works")
    
    def test_delete(self, test_memory):
        """Test delete"""
        test_memory.store('delete_me', 'value')
        test_memory.delete('delete_me')
        result = test_memory.retrieve('delete_me')
        assert result['success'] == False
        print("✓ MemoryManager delete works")
    
    def test_list_keys(self, test_memory):
        """Test list keys"""
        test_memory.store('key1', 'val1', 'test')
        test_memory.store('key2', 'val2', 'test')
        result = test_memory.list_keys('test')
        assert result['success'] == True
        assert len(result['keys']) >= 2
        print("✓ MemoryManager list_keys works")
    
    def test_add_to_history(self, test_memory):
        """Test history"""
        test_memory.add_to_history('outfit', {'rating': 5})
        history = test_memory.get_history('outfit')
        assert history['success'] == True
        assert len(history['events']) == 1
        print("✓ MemoryManager history works")


# ============================================================================
# TEST SESSION SERVICE
# ============================================================================

class TestSessionService:
    """Test Session Service"""
    
    def test_initialization(self):
        """Test session initialization"""
        service = SessionService(session_timeout_minutes=30)
        assert service.name == "SessionService"
        print("✓ SessionService initialized")
    
    def test_create_session(self):
        """Test session creation"""
        service = SessionService()
        result = service.create_session('user123')
        assert result['success'] == True
        assert 'session_id' in result
        print("✓ SessionService create_session works")
    
    def test_get_session(self):
        """Test get session"""
        service = SessionService()
        create_result = service.create_session('user123')
        session_id = create_result['session_id']
        get_result = service.get_session(session_id)
        assert get_result['success'] == True
        assert get_result['session']['user_id'] == 'user123'
        print("✓ SessionService get_session works")
    
    def test_update_session(self):
        """Test update session"""
        service = SessionService()
        create_result = service.create_session()
        session_id = create_result['session_id']
        service.update_session(session_id, 'outfit_count', 5)
        get_result = service.get_session(session_id)
        assert get_result['session']['data']['outfit_count'] == 5
        print("✓ SessionService update_session works")
    
    def test_end_session(self):
        """Test end session"""
        service = SessionService()
        create_result = service.create_session()
        session_id = create_result['session_id']
        end_result = service.end_session(session_id)
        assert end_result['success'] == True
        get_result = service.get_session(session_id)
        assert get_result['success'] == False
        print("✓ SessionService end_session works")
    
    def test_get_stats(self):
        """Test session stats"""
        service = SessionService()
        service.create_session()
        service.create_session()
        result = service.get_stats()
        assert result['success'] == True
        assert result['stats']['total_sessions'] == 2
        print("✓ SessionService get_stats works")


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all tool tests"""
    print("\n" + "="*70)
    print("🧪 AI FASHION CONSULTANT - COMPLETE TOOLS TEST SUITE")
    print("="*70 + "\n")
    
    exit_code = pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--color=yes",
        "-ra"
    ])
    
    print("\n" + "="*70)
    if exit_code == 0:
        print("✅ ALL TESTS PASSED! Tools are production-ready.")
        print("   - ImageTagger: ✓")
        print("   - WardrobeDB: ✓")
        print("   - WeatherAPI: ✓")
        print("   - ColorMatcher: ✓")
        print("   - GenderStyleRules: ✓")
        print("   - CalendarReader: ✓")
        print("   - MemoryManager: ✓")
        print("   - SessionService: ✓")
    else:
        print("❌ SOME TESTS FAILED - Review output above")
    print("="*70 + "\n")
    
    return exit_code


if __name__ == "__main__":
    run_all_tests()