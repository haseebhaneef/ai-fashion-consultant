"""Wardrobe database manager"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from config.settings import DATABASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WardrobeDB:
    """Manages wardrobe database operations"""
    
    def __init__(self, db_path: str = "data/wardrobe.db"):
        self.db_path = db_path
        self.init_db()
        logger.info(f"✓ WardrobeDB initialized: {db_path}")
    
    def init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Wardrobe items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wardrobe_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                garment_type TEXT NOT NULL,
                color TEXT NOT NULL,
                secondary_colors TEXT,
                pattern TEXT,
                formality TEXT,
                season TEXT,
                material TEXT,
                style_tags TEXT,
                brand TEXT,
                condition TEXT,
                image_path TEXT,
                times_worn INTEGER DEFAULT 0,
                last_worn DATE,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags_json TEXT
            )
        """)
        
        # Outfits table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outfits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                outfit_json TEXT NOT NULL,
                occasion TEXT,
                weather TEXT,
                temperature REAL,
                gender TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                user_feedback TEXT,
                rating INTEGER,
                worn_date DATE
            )
        """)
        
        # User preferences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gender TEXT,
                favorite_colors TEXT,
                disliked_colors TEXT,
                preferred_styles TEXT,
                sizes TEXT,
                preferences_json TEXT,
                updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Feedback history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                outfit_id INTEGER,
                feedback_type TEXT,
                feedback_text TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (outfit_id) REFERENCES outfits(id)
            )
        """)
        
        conn.commit()
        conn.close()
        logger.info("✓ Database schema initialized")
    
    def add_item(self, tags: dict) -> int:
        """Add wardrobe item"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO wardrobe_items (
                garment_type, color, secondary_colors, pattern, formality,
                season, material, style_tags, brand, condition, image_path, tags_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tags.get('garment_type'),
            tags.get('color'),
            json.dumps(tags.get('secondary_colors', [])),
            tags.get('pattern'),
            tags.get('formality'),
            json.dumps(tags.get('season', [])),
            tags.get('material'),
            json.dumps(tags.get('style_tags', [])),
            tags.get('brand'),
            tags.get('condition'),
            tags.get('image_path'),
            json.dumps(tags)
        ))
        
        item_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(f"✓ Added item #{item_id}: {tags.get('garment_type')}")
        return item_id
    
    def get_all_items(self) -> List[Dict]:
        """Get all wardrobe items with full tag details"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM wardrobe_items ORDER BY added_date DESC")
        rows = cursor.fetchall()
        
        items = []
        for row in rows:
            item = dict(row)
            # Load standard list fields
            item['secondary_colors'] = json.loads(item['secondary_colors'] or '[]')
            item['season'] = json.loads(item['season'] or '[]')
            item['style_tags'] = json.loads(item['style_tags'] or '[]')
            
            # Merge detailed tags from tags_json if available
            # This allows the Planner to see 'gender_category' and other new fields
            if item.get('tags_json'):
                try:
                    detailed_tags = json.loads(item['tags_json'])
                    # Update item with details, but don't overwrite id/image_path
                    for k, v in detailed_tags.items():
                        if k not in ['id', 'image_path', 'added_date']:
                            item[k] = v
                except:
                    pass
            
            items.append(item)
        
        conn.close()
        return items
    
    def get_items_by_type(self, garment_type: str) -> List[Dict]:
        """Get items by type"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM wardrobe_items WHERE garment_type = ?", (garment_type,))
        rows = cursor.fetchall()
        
        items = [dict(row) for row in rows]
        conn.close()
        return items
    
    def get_items_by_occasion(self, formality: str, season: str = None) -> List[Dict]:
        """Get items suitable for occasion"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if season:
            cursor.execute("""
                SELECT * FROM wardrobe_items 
                WHERE formality = ? AND season LIKE ?
            """, (formality, f'%{season}%'))
        else:
            cursor.execute("SELECT * FROM wardrobe_items WHERE formality = ?", (formality,))
        
        rows = cursor.fetchall()
        items = []
        for row in rows:
            item = dict(row)
            item['season'] = json.loads(item['season'] or '[]')
            items.append(item)
        
        conn.close()
        return items
    
    def save_outfit(self, outfit: dict, metadata: dict) -> int:
        """Save generated outfit"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO outfits (
                outfit_json, occasion, weather, temperature, gender
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            json.dumps(outfit),
            metadata.get('occasion'),
            metadata.get('weather'),
            metadata.get('temperature'),
            metadata.get('gender')
        ))
        
        outfit_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return outfit_id
    
    def save_feedback(self, outfit_id: int, feedback: dict):
        """Save user feedback"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE outfits 
            SET user_feedback = ?, rating = ?
            WHERE id = ?
        """, (
            feedback.get('feedback_text'),
            feedback.get('rating'),
            outfit_id
        ))
        
        cursor.execute("""
            INSERT INTO feedback_history (
                outfit_id, feedback_type, feedback_text
            ) VALUES (?, ?, ?)
        """, (
            outfit_id,
            feedback.get('feedback_type'),
            feedback.get('feedback_text')
        ))
        
        conn.commit()
        conn.close()

    def get_user_preferences(self) -> dict:
        """Get user preferences"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM user_preferences ORDER BY updated_date DESC LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            prefs = dict(row)
            prefs['favorite_colors'] = json.loads(prefs['favorite_colors'] or '[]')
            prefs['disliked_colors'] = json.loads(prefs['disliked_colors'] or '[]')
            prefs['preferred_styles'] = json.loads(prefs['preferred_styles'] or '[]')
        else:
            prefs = {
                'gender': 'unisex',
                'favorite_colors': [],
                'disliked_colors': [],
                'preferred_styles': [],
                'sizes': json.dumps({}),
                'preferences_json': '{}'
            }
        
        conn.close()
        return prefs
    
    def update_preferences(self, preferences: dict):
        """Update user preferences"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO user_preferences (
                gender, favorite_colors, disliked_colors, 
                preferred_styles, sizes, preferences_json
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            preferences.get('gender'),
            json.dumps(preferences.get('favorite_colors', [])),
            json.dumps(preferences.get('disliked_colors', [])),
            json.dumps(preferences.get('preferred_styles', [])),
            json.dumps(preferences.get('sizes', {})),
            json.dumps(preferences)
        ))
        
        conn.commit()
        conn.close()
    
    def get_wardrobe_stats(self) -> dict:
        """Get wardrobe statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as total FROM wardrobe_items")
        total = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT garment_type, COUNT(*) as count 
            FROM wardrobe_items 
            GROUP BY garment_type
        """)
        by_type = dict(cursor.fetchall())
        
        cursor.execute("""
            SELECT AVG(times_worn) as avg_worn FROM wardrobe_items
        """)
        avg_worn = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_items': total,
            'by_type': by_type,
            'average_times_worn': round(avg_worn, 2)
        }

    def delete_item(self, item_id: int) -> bool:
        """Delete an item from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM wardrobe_items WHERE id = ?", (item_id,))
            rows_affected = cursor.rowcount
            conn.commit()
            conn.close()
            logger.info(f"✓ Deleted item #{item_id}")
            return rows_affected > 0
        except Exception as e:
            logger.error(f"✗ Error deleting item: {e}")
            return False

    def get_recent_outfits(self, limit: int = 5) -> list:
        """Get recently generated outfits"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT outfit_json 
                FROM outfits 
                ORDER BY created_date DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            outfits = []
            for row in rows:
                try:
                    data = json.loads(row['outfit_json'])
                    outfits.append(data)
                except:
                    pass
            
            conn.close()
            return outfits
        except Exception as e:
            logger.error(f"Error fetching recent outfits: {e}")
            return []
            
    def mark_outfit_as_worn(self, outfit_id: int) -> bool:
        """Mark an outfit as worn today"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            today = datetime.now().date().isoformat()
            
            cursor.execute("""
                UPDATE outfits 
                SET worn_date = ?
                WHERE id = ?
            """, (today, outfit_id))
            
            conn.commit()
            conn.close()
            logger.info(f"✓ Outfit #{outfit_id} marked as worn on {today}")
            return True
        except Exception as e:
            logger.error(f"✗ Error marking outfit worn: {e}")
            return False

    def get_outfits_worn_today(self) -> list:
        """Get outfits marked as worn today"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            today = datetime.now().date().isoformat()
            
            cursor.execute("""
                SELECT outfit_json 
                FROM outfits 
                WHERE worn_date = ?
            """, (today,))
            
            rows = cursor.fetchall()
            outfits = []
            for row in rows:
                try:
                    data = json.loads(row['outfit_json'])
                    outfits.append(data)
                except:
                    pass
            
            conn.close()
            return outfits
        except Exception as e:
            logger.error(f"Error fetching worn outfits: {e}")
            return []