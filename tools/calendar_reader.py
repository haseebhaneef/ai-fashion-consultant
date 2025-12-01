"""Calendar Reader Tool - Google Calendar integration"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CalendarReader:
    """
    Reads calendar events to provide context for outfit recommendations
    Integrates with Google Calendar API (mock implementation included)
    """
    
    def __init__(self, credentials_path: str = None):
        self.name = "CalendarReader"
        self.credentials_path = credentials_path
        self.connected = False
        
        # Try to connect to real calendar
        if credentials_path:
            try:
                self._initialize_calendar()
                self.connected = True
            except Exception as e:
                logger.warning(f"[{self.name}] Could not connect to calendar: {str(e)}")
                logger.info(f"[{self.name}] Using mock calendar data")
        
        logger.info(f"✓ {self.name} initialized (Mock mode: {not self.connected})")
    
    def _initialize_calendar(self):
        """Initialize Google Calendar API connection"""
        # In production, this would use google-auth and googleapiclient
        # For now, we'll use mock data
        pass
    
    def get_todays_events(self) -> Dict:
        """
        Get today's calendar events
        
        Returns:
            dict: Today's events with occasion detection
        """
        logger.info(f"[{self.name}] Fetching today's events")
        
        try:
            if self.connected:
                events = self._fetch_real_events()
            else:
                events = self._get_mock_events()
            
            # Analyze events for outfit context
            occasion = self._determine_occasion(events)
            
            result = {
                'success': True,
                'tool': self.name,
                'date': datetime.now().strftime('%Y-%m-%d'),
                'events': events,
                'occasion': occasion,
                'event_count': len(events),
                'message': f"Found {len(events)} events for today"
            }
            
            logger.info(f"[{self.name}] ✓ Retrieved {len(events)} events, occasion: {occasion}")
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error fetching events: {str(e)}")
            return {
                'success': False,
                'tool': self.name,
                'events': [],
                'message': f"Error: {str(e)}"
            }
    
    def get_upcoming_events(self, days: int = 7) -> Dict:
        """
        Get upcoming events for the next N days
        
        Args:
            days: Number of days to look ahead
            
        Returns:
            dict: Upcoming events
        """
        logger.info(f"[{self.name}] Fetching events for next {days} days")
        
        try:
            if self.connected:
                events = self._fetch_real_events(days=days)
            else:
                events = self._get_mock_events(days=days)
            
            result = {
                'success': True,
                'tool': self.name,
                'date_range': f"{datetime.now().strftime('%Y-%m-%d')} to {(datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')}",
                'events': events,
                'event_count': len(events),
                'message': f"Found {len(events)} upcoming events"
            }
            
            logger.info(f"[{self.name}] ✓ Retrieved {len(events)} upcoming events")
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error: {str(e)}")
            return {
                'success': False,
                'tool': self.name,
                'events': [],
                'message': f"Error: {str(e)}"
            }
    
    def _fetch_real_events(self, days: int = 1) -> List[Dict]:
        """Fetch events from real Google Calendar API"""
        # Production implementation would use:
        # from googleapiclient.discovery import build
        # service = build('calendar', 'v3', credentials=creds)
        # events = service.events().list(...).execute()
        
        # For now, return empty list
        return []
    
    def _get_mock_events(self, days: int = 1) -> List[Dict]:
        """Generate mock calendar events for demonstration"""
        mock_events = []
        
        # Today's events
        if days >= 1:
            today = datetime.now()
            
            # Morning meeting
            if today.hour < 10:
                mock_events.append({
                    'summary': 'Team Standup',
                    'start': today.replace(hour=9, minute=0).isoformat(),
                    'end': today.replace(hour=9, minute=30).isoformat(),
                    'type': 'work',
                    'formality': 'business_casual'
                })
            
            # Afternoon client meeting
            if today.hour < 14:
                mock_events.append({
                    'summary': 'Client Presentation',
                    'start': today.replace(hour=14, minute=0).isoformat(),
                    'end': today.replace(hour=15, minute=0).isoformat(),
                    'type': 'work',
                    'formality': 'formal'
                })
            
            # Evening event (random)
            if today.weekday() == 4:  # Friday
                mock_events.append({
                    'summary': 'Happy Hour with Friends',
                    'start': today.replace(hour=18, minute=0).isoformat(),
                    'end': today.replace(hour=20, minute=0).isoformat(),
                    'type': 'social',
                    'formality': 'casual'
                })
        
        # Weekend events
        if days > 1:
            tomorrow = datetime.now() + timedelta(days=1)
            if tomorrow.weekday() == 5:  # Saturday
                mock_events.append({
                    'summary': 'Brunch with Family',
                    'start': tomorrow.replace(hour=11, minute=0).isoformat(),
                    'end': tomorrow.replace(hour=13, minute=0).isoformat(),
                    'type': 'casual',
                    'formality': 'casual'
                })
        
        return mock_events
    
    def _determine_occasion(self, events: List[Dict]) -> str:
        """
        Determine the most formal occasion for the day
        
        Args:
            events: List of calendar events
            
        Returns:
            str: Occasion type
        """
        if not events:
            return 'casual'
        
        # Rank formality
        formality_rank = {
            'formal': 4,
            'business_casual': 3,
            'smart_casual': 2,
            'casual': 1
        }
        
        # Find most formal event
        max_formality = 0
        occasion = 'casual'
        
        for event in events:
            formality = event.get('formality', 'casual')
            rank = formality_rank.get(formality, 1)
            
            if rank > max_formality:
                max_formality = rank
                
                # Map formality to occasion
                if formality == 'formal':
                    occasion = 'formal'
                elif formality == 'business_casual':
                    occasion = 'work'
                else:
                    occasion = event.get('type', 'casual')
        
        return occasion
    
    def search_events(self, query: str, days: int = 30) -> Dict:
        """
        Search for events matching a query
        
        Args:
            query: Search query
            days: Days to search
            
        Returns:
            dict: Matching events
        """
        logger.info(f"[{self.name}] Searching for '{query}'")
        
        events = self._get_mock_events(days=days)
        
        # Filter events
        matching = [
            event for event in events
            if query.lower() in event.get('summary', '').lower()
        ]
        
        return {
            'success': True,
            'tool': self.name,
            'query': query,
            'matches': matching,
            'count': len(matching),
            'message': f"Found {len(matching)} matching events"
        }


# Test
if __name__ == "__main__":
    reader = CalendarReader()
    
    # Test today's events
    print("--- Today's Events ---")
    result = reader.get_todays_events()
    print(f"Events: {result['event_count']}")
    print(f"Occasion: {result['occasion']}")
    for event in result['events']:
        print(f"  - {event['summary']} ({event['formality']})")
    
    # Test upcoming events
    print("\n--- Upcoming Events ---")
    result = reader.get_upcoming_events(days=7)
    print(f"Events: {result['event_count']}")