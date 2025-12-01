"""Session Service - Manages user sessions"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionService:
    """
    Manages user sessions and temporary state
    Handles session lifecycle and cleanup
    """
    
    def __init__(self, session_timeout_minutes: int = 60):
        self.name = "SessionService"
        self.sessions = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        logger.info(f"✓ {self.name} initialized (timeout: {session_timeout_minutes}min)")
    
    def create_session(self, user_id: Optional[str] = None) -> Dict:
        """
        Create a new session
        
        Args:
            user_id: Optional user identifier
            
        Returns:
            dict: Session details
        """
        session_id = str(uuid.uuid4())
        
        session = {
            'session_id': session_id,
            'user_id': user_id or 'anonymous',
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'data': {},
            'active': True
        }
        
        self.sessions[session_id] = session
        
        logger.info(f"[{self.name}] ✓ Created session: {session_id}")
        
        return {
            'success': True,
            'service': self.name,
            'session_id': session_id,
            'message': 'Session created successfully'
        }
    
    def get_session(self, session_id: str) -> Dict:
        """Get session data"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            
            # Check if session expired
            if self._is_expired(session):
                self.end_session(session_id)
                return {
                    'success': False,
                    'service': self.name,
                    'message': 'Session expired'
                }
            
            # Update last activity
            session['last_activity'] = datetime.now()
            
            return {
                'success': True,
                'service': self.name,
                'session': session,
                'message': 'Session retrieved'
            }
        else:
            return {
                'success': False,
                'service': self.name,
                'message': 'Session not found'
            }
    
    def update_session(self, session_id: str, key: str, value: any) -> Dict:
        """Update session data"""
        if session_id in self.sessions:
            self.sessions[session_id]['data'][key] = value
            self.sessions[session_id]['last_activity'] = datetime.now()
            
            return {
                'success': True,
                'service': self.name,
                'message': 'Session updated'
            }
        else:
            return {
                'success': False,
                'service': self.name,
                'message': 'Session not found'
            }
    
    def end_session(self, session_id: str) -> Dict:
        """End a session"""
        if session_id in self.sessions:
            self.sessions[session_id]['active'] = False
            del self.sessions[session_id]
            
            logger.info(f"[{self.name}] ✓ Ended session: {session_id}")
            
            return {
                'success': True,
                'service': self.name,
                'message': 'Session ended'
            }
        else:
            return {
                'success': False,
                'service': self.name,
                'message': 'Session not found'
            }
    
    def _is_expired(self, session: Dict) -> bool:
        """Check if session is expired"""
        return datetime.now() - session['last_activity'] > self.session_timeout
    
    def cleanup_expired(self) -> Dict:
        """Clean up expired sessions"""
        expired = [
            sid for sid, session in self.sessions.items()
            if self._is_expired(session)
        ]
        
        for sid in expired:
            del self.sessions[sid]
        
        logger.info(f"[{self.name}] ✓ Cleaned up {len(expired)} expired sessions")
        
        return {
            'success': True,
            'service': self.name,
            'cleaned_up': len(expired),
            'message': f"Removed {len(expired)} expired sessions"
        }
    
    def get_stats(self) -> Dict:
        """Get session statistics"""
        active = sum(1 for s in self.sessions.values() if s['active'])
        
        return {
            'success': True,
            'service': self.name,
            'stats': {
                'total_sessions': len(self.sessions),
                'active_sessions': active,
                'timeout_minutes': self.session_timeout.seconds // 60
            },
            'message': 'Statistics retrieved'
        }


# Test
if __name__ == "__main__":
    service = SessionService(session_timeout_minutes=30)
    
    # Create session
    result = service.create_session('user123')
    session_id = result['session_id']
    print(f"Created session: {session_id}")
    
    # Update session
    service.update_session(session_id, 'outfit_count', 5)
    
    # Get session
    result = service.get_session(session_id)
    print(f"Session data: {result['session']['data']}")
    
    # Stats
    stats = service.get_stats()
    print(f"Stats: {stats['stats']}")