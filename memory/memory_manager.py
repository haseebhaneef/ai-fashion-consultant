"""Memory Manager - Long-term memory persistence"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MemoryManager:
    """
    Manages long-term memory storage and retrieval
    Persists user preferences, history, and learned patterns
    """
    
    def __init__(self, storage_path: str = "data/memory.json"):
        self.name = "MemoryManager"
        self.storage_path = Path(storage_path)
        self.memory = {}
        
        # Ensure directory exists
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing memory
        self._load_memory()
        
        logger.info(f"✓ {self.name} initialized with storage: {storage_path}")
    
    def _load_memory(self):
        """Load memory from disk"""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r') as f:
                    self.memory = json.load(f)
                logger.info(f"[{self.name}] ✓ Loaded memory from disk")
            else:
                self.memory = self._initialize_empty_memory()
                self._save_memory()
                logger.info(f"[{self.name}] ✓ Initialized new memory")
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error loading memory: {str(e)}")
            self.memory = self._initialize_empty_memory()
    
    def _save_memory(self):
        """Save memory to disk"""
        try:
            with open(self.storage_path, 'w') as f:
                json.dump(self.memory, f, indent=2)
            logger.info(f"[{self.name}] ✓ Memory saved to disk")
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error saving memory: {str(e)}")
    
    def _initialize_empty_memory(self) -> Dict:
        """Initialize empty memory structure"""
        return {
            'user_profile': {
                'gender': 'unisex',
                'sizes': {},
                'created_at': datetime.now().isoformat()
            },
            'preferences': {
                'favorite_colors': [],
                'disliked_colors': [],
                'preferred_styles': [],
                'avoided_patterns': []
            },
            'outfit_history': [],
            'feedback_history': [],
            'learned_patterns': {},
            'metadata': {
                'version': '1.0',
                'last_updated': datetime.now().isoformat()
            }
        }
    
    def store(self, key: str, value: any, namespace: str = 'default') -> Dict:
        """
        Store a value in memory
        
        Args:
            key: Memory key
            value: Value to store
            namespace: Memory namespace
            
        Returns:
            dict: Operation result
        """
        logger.info(f"[{self.name}] Storing '{key}' in namespace '{namespace}'")
        
        try:
            if namespace not in self.memory:
                self.memory[namespace] = {}
            
            self.memory[namespace][key] = {
                'value': value,
                'stored_at': datetime.now().isoformat()
            }
            
            self._update_metadata()
            self._save_memory()
            
            return {
                'success': True,
                'manager': self.name,
                'key': key,
                'namespace': namespace,
                'message': 'Value stored successfully'
            }
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error storing: {str(e)}")
            return {
                'success': False,
                'manager': self.name,
                'message': f"Error: {str(e)}"
            }
    
    def retrieve(self, key: str, namespace: str = 'default') -> Dict:
        """
        Retrieve a value from memory
        
        Args:
            key: Memory key
            namespace: Memory namespace
            
        Returns:
            dict: Retrieved value or None
        """
        logger.info(f"[{self.name}] Retrieving '{key}' from namespace '{namespace}'")
        
        try:
            if namespace in self.memory and key in self.memory[namespace]:
                data = self.memory[namespace][key]
                
                return {
                    'success': True,
                    'manager': self.name,
                    'key': key,
                    'namespace': namespace,
                    'value': data['value'],
                    'stored_at': data['stored_at'],
                    'message': 'Value retrieved successfully'
                }
            else:
                return {
                    'success': False,
                    'manager': self.name,
                    'key': key,
                    'value': None,
                    'message': 'Key not found'
                }
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error retrieving: {str(e)}")
            return {
                'success': False,
                'manager': self.name,
                'message': f"Error: {str(e)}"
            }
    
    def delete(self, key: str, namespace: str = 'default') -> Dict:
        """Delete a value from memory"""
        logger.info(f"[{self.name}] Deleting '{key}' from namespace '{namespace}'")
        
        try:
            if namespace in self.memory and key in self.memory[namespace]:
                del self.memory[namespace][key]
                self._update_metadata()
                self._save_memory()
                
                return {
                    'success': True,
                    'manager': self.name,
                    'message': 'Value deleted successfully'
                }
            else:
                return {
                    'success': False,
                    'manager': self.name,
                    'message': 'Key not found'
                }
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error deleting: {str(e)}")
            return {
                'success': False,
                'manager': self.name,
                'message': f"Error: {str(e)}"
            }
    
    def list_keys(self, namespace: str = 'default') -> Dict:
        """List all keys in a namespace"""
        try:
            if namespace in self.memory:
                keys = list(self.memory[namespace].keys())
            else:
                keys = []
            
            return {
                'success': True,
                'manager': self.name,
                'namespace': namespace,
                'keys': keys,
                'count': len(keys),
                'message': f"Found {len(keys)} keys"
            }
        except Exception as e:
            return {
                'success': False,
                'manager': self.name,
                'message': f"Error: {str(e)}"
            }
    
    def add_to_history(self, event_type: str, data: Dict) -> Dict:
        """Add event to history"""
        logger.info(f"[{self.name}] Adding {event_type} to history")
        
        try:
            history_key = f"{event_type}_history"
            
            if history_key not in self.memory:
                self.memory[history_key] = []
            
            event = {
                'type': event_type,
                'data': data,
                'timestamp': datetime.now().isoformat()
            }
            
            self.memory[history_key].append(event)
            
            # Keep only last 100 events
            if len(self.memory[history_key]) > 100:
                self.memory[history_key] = self.memory[history_key][-100:]
            
            self._update_metadata()
            self._save_memory()
            
            return {
                'success': True,
                'manager': self.name,
                'message': 'Event added to history'
            }
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error: {str(e)}")
            return {
                'success': False,
                'manager': self.name,
                'message': f"Error: {str(e)}"
            }
    
    def get_history(self, event_type: str, limit: int = 50) -> Dict:
        """Get history events"""
        history_key = f"{event_type}_history"
        
        if history_key in self.memory:
            events = self.memory[history_key][-limit:]
        else:
            events = []
        
        return {
            'success': True,
            'manager': self.name,
            'event_type': event_type,
            'events': events,
            'count': len(events),
            'message': f"Retrieved {len(events)} events"
        }
    
    def _update_metadata(self):
        """Update memory metadata"""
        if 'metadata' not in self.memory:
            self.memory['metadata'] = {}
        
        self.memory['metadata']['last_updated'] = datetime.now().isoformat()
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        stats = {
            'namespaces': len([k for k in self.memory.keys() if not k.startswith('_')]),
            'total_keys': sum(len(v) if isinstance(v, dict) else 0 for v in self.memory.values()),
            'storage_path': str(self.storage_path),
            'last_updated': self.memory.get('metadata', {}).get('last_updated', 'Never')
        }
        
        return {
            'success': True,
            'manager': self.name,
            'stats': stats,
            'message': 'Statistics retrieved'
        }
    
    def clear_all(self) -> Dict:
        """Clear all memory (use with caution!)"""
        logger.warning(f"[{self.name}] Clearing all memory!")
        
        self.memory = self._initialize_empty_memory()
        self._save_memory()
        
        return {
            'success': True,
            'manager': self.name,
            'message': 'All memory cleared'
        }


# Test
if __name__ == "__main__":
    manager = MemoryManager("data/test_memory.json")
    
    # Store values
    print("--- Storing Values ---")
    manager.store('favorite_color', 'blue', 'preferences')
    manager.store('last_outfit', {'top': 'shirt', 'bottom': 'pants'}, 'outfits')
    
    # Retrieve values
    print("\n--- Retrieving Values ---")
    result = manager.retrieve('favorite_color', 'preferences')
    print(f"Favorite color: {result.get('value')}")
    
    # List keys
    print("\n--- Listing Keys ---")
    result = manager.list_keys('preferences')
    print(f"Keys in preferences: {result['keys']}")
    
    # Add to history
    print("\n--- Adding to History ---")
    manager.add_to_history('outfit', {'rating': 5})
    
    # Get stats
    print("\n--- Memory Stats ---")
    stats = manager.get_stats()
    print(f"Stats: {stats['stats']}")