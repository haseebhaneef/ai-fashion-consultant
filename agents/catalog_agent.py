"""Catalog Agent - Wardrobe database management"""

import logging
from tools.wardrobe_db import WardrobeDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CatalogAgent:
    """
    Manages wardrobe database operations
    Stores, retrieves, and organizes clothing items
    """
    
    def __init__(self):
        self.name = "CatalogAgent"
        self.db = WardrobeDB()
        logger.info(f"✓ {self.name} initialized")
    
    def add_to_wardrobe(self, garment_data: dict) -> dict:
        """Add new item to wardrobe"""
        logger.info(f"[{self.name}] Adding item to wardrobe")
        try:
            item_id = self.db.add_item(garment_data)
            return {
                'success': True,
                'agent': self.name,
                'item_id': item_id,
                'message': f"Added {garment_data.get('garment_type')} to wardrobe (ID: {item_id})"
            }
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error adding item: {str(e)}")
            return {'success': False, 'agent': self.name, 'item_id': None, 'message': f"Error: {str(e)}"}
    
    def get_wardrobe(self, filters: dict = None) -> dict:
        """Retrieve wardrobe items with optional filters"""
        logger.info(f"[{self.name}] Retrieving wardrobe items")
        try:
            items = self.db.get_all_items()
            
            if filters:
                if filters.get('garment_type'):
                    items = [i for i in items if i['garment_type'] == filters['garment_type']]
                if filters.get('formality'):
                    items = [i for i in items if i['formality'] == filters['formality']]
                if filters.get('season'):
                    season = filters['season']
                    items = [i for i in items if season in i.get('season', [])]
                if filters.get('color'):
                    color = filters['color'].lower()
                    items = [i for i in items if color in i['color'].lower()]
            
            return {
                'success': True,
                'agent': self.name,
                'items': items,
                'count': len(items),
                'filters_applied': filters or {},
                'message': f"Retrieved {len(items)} items"
            }
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error retrieving items: {str(e)}")
            return {'success': False, 'agent': self.name, 'items': [], 'count': 0, 'message': f"Error: {str(e)}"}
    
    def get_items_by_category(self, category: str) -> dict:
        """Get all items of a specific category"""
        logger.info(f"[{self.name}] Getting {category} items")
        try:
            items = self.db.get_items_by_type(category)
            return {
                'success': True,
                'agent': self.name,
                'category': category,
                'items': items,
                'count': len(items),
                'message': f"Found {len(items)} {category} items"
            }
        except Exception as e:
            logger.error(f"[{self.name}] Error: {str(e)}")
            return {'success': False, 'agent': self.name, 'items': [], 'message': f"Error: {str(e)}"}
    
    def get_wardrobe_stats(self) -> dict:
        """Get wardrobe statistics and analytics"""
        logger.info(f"[{self.name}] Calculating wardrobe statistics")
        try:
            stats = self.db.get_wardrobe_stats()
            return {
                'success': True,
                'agent': self.name,
                'stats': stats,
                'message': "Statistics calculated successfully"
            }
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error calculating stats: {str(e)}")
            return {'success': False, 'agent': self.name, 'stats': {}, 'message': f"Error: {str(e)}"}
    
    def analyze_wardrobe_coverage(self) -> dict:
        """Analyze what types of items are well-covered vs gaps"""
        logger.info(f"[{self.name}] Analyzing wardrobe coverage")
        try:
            all_items = self.db.get_all_items()
            
            categories = {}
            for item in all_items:
                cat = item['garment_type']
                categories[cat] = categories.get(cat, 0) + 1
            
            ideal_minimums = {'shirt': 5, 'pants': 3, 'shoes': 3, 'dress': 2, 'outerwear': 2}
            gaps = {}
            for cat, minimum in ideal_minimums.items():
                current = categories.get(cat, 0)
                if current < minimum:
                    gaps[cat] = minimum - current
            
            coverage_score = max(0, 1 - (len(gaps) / len(ideal_minimums)))
            
            return {
                'success': True,
                'agent': self.name,
                'coverage_by_category': categories,
                'gaps': gaps,
                'coverage_score': round(coverage_score, 2),
                'message': f"Coverage score: {round(coverage_score * 100)}%"
            }
        except Exception as e:
            logger.error(f"[{self.name}] Error: {str(e)}")
            return {'success': False, 'agent': self.name, 'message': f"Error: {str(e)}"}

    def delete_item(self, item_id: int) -> dict:
        """Delete item from wardrobe"""
        logger.info(f"[{self.name}] Deleting item #{item_id}")
        try:
            success = self.db.delete_item(item_id)
            if success:
                return {'success': True, 'agent': self.name, 'message': f"Item #{item_id} deleted successfully"}
            else:
                return {'success': False, 'agent': self.name, 'message': f"Item #{item_id} not found"}
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error: {str(e)}")
            return {'success': False, 'agent': self.name, 'message': f"Error: {str(e)}"}

    def get_recent_outfits(self, limit: int = 5) -> dict:
        """Get recent outfits to avoid repetition"""
        outfits = self.db.get_recent_outfits(limit)
        return {'success': True, 'outfits': outfits}

    def save_generated_outfit(self, outfit: dict, metadata: dict) -> dict:
        """Save a generated outfit to history"""
        try:
            outfit_id = self.db.save_outfit(outfit, metadata)
            return {'success': True, 'outfit_id': outfit_id}
        except Exception as e:
            logger.error(f"Error saving outfit: {e}")
            return {'success': False, 'message': str(e)}

    # --- NEW METHODS ---
    def mark_outfit_worn(self, outfit_id: int) -> dict:
        """Mark outfit as worn today"""
        success = self.db.mark_outfit_as_worn(outfit_id)
        return {'success': success, 'agent': self.name}

    def get_outfits_worn_today(self) -> dict:
        """Get outfits worn today"""
        outfits = self.db.get_outfits_worn_today()
        return {'success': True, 'outfits': outfits}

    def get_agent_status(self) -> dict:
        """Get agent status"""
        return {
            'name': self.name,
            'status': 'active',
            'capabilities': ['add_items', 'retrieve_items', 'delete_items', 'filter_wardrobe', 'calculate_statistics', 'database_management', 'history_tracking'],
            'database': 'connected',
            'ready': True
        }