"""Loop Agent - Daily routine and long-running tasks"""

import logging
import time
from datetime import datetime, timedelta
from typing import Callable

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LoopAgent:
    """
    Manages recurring tasks and daily routines
    Runs scheduled operations like morning outfit generation
    """
    
    def __init__(self):
        self.name = "LoopAgent"
        self.running = False
        self.tasks = []
        logger.info(f"✓ {self.name} initialized")
    
    def schedule_daily_outfit(self, time_str: str, callback: Callable) -> dict:
        """
        Schedule daily outfit generation
        
        Args:
            time_str: Time in HH:MM format (e.g., "07:00")
            callback: Function to call for outfit generation
            
        Returns:
            dict: Schedule confirmation
        """
        logger.info(f"[{self.name}] Scheduling daily outfit at {time_str}")
        
        try:
            hour, minute = map(int, time_str.split(':'))
            
            task = {
                'name': 'daily_outfit',
                'time': time_str,
                'hour': hour,
                'minute': minute,
                'callback': callback,
                'last_run': None,
                'enabled': True
            }
            
            self.tasks.append(task)
            
            result = {
                'success': True,
                'agent': self.name,
                'task': 'daily_outfit',
                'scheduled_time': time_str,
                'message': f"Daily outfit scheduled for {time_str}"
            }
            
            logger.info(f"[{self.name}] ✓ Daily outfit scheduled: {time_str}")
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error scheduling task: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'message': f"Error: {str(e)}"
            }
    
    def run_morning_routine(self, wardrobe_items: list, user_profile: dict) -> dict:
        """
        Execute morning outfit routine
        
        Args:
            wardrobe_items: User's wardrobe
            user_profile: User preferences
            
        Returns:
            dict: Morning outfit recommendation
        """
        logger.info(f"[{self.name}] Running morning routine")
        
        try:
            from agents.planner_agent import PlannerAgent
            
            # Initialize planner
            planner = PlannerAgent()
            
            # Generate daily outfit
            outfit = planner.get_daily_outfit(wardrobe_items, user_profile)
            
            result = {
                'success': True,
                'agent': self.name,
                'routine': 'morning_outfit',
                'outfit': outfit,
                'timestamp': datetime.now().isoformat(),
                'message': 'Morning outfit generated'
            }
            
            logger.info(f"[{self.name}] ✓ Morning routine complete")
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error in morning routine: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'message': f"Error: {str(e)}"
            }
    
    def run_seasonal_rotation(self, wardrobe_items: list, current_season: str) -> dict:
        """
        Rotate wardrobe items based on season
        
        Args:
            wardrobe_items: All wardrobe items
            current_season: Current season (spring/summer/fall/winter)
            
        Returns:
            dict: Rotation recommendations
        """
        logger.info(f"[{self.name}] Running seasonal rotation for {current_season}")
        
        try:
            # Filter items by season
            active_items = []
            storage_items = []
            
            for item in wardrobe_items:
                seasons = item.get('season', [])
                if isinstance(seasons, str):
                    seasons = [seasons]
                
                if current_season.lower() in [s.lower() for s in seasons]:
                    active_items.append(item)
                else:
                    storage_items.append(item)
            
            # Identify rarely worn items
            rarely_worn = [
                item for item in wardrobe_items 
                if item.get('times_worn', 0) < 2
            ]
            
            result = {
                'success': True,
                'agent': self.name,
                'season': current_season,
                'active_items': len(active_items),
                'storage_items': len(storage_items),
                'rarely_worn': len(rarely_worn),
                'recommendations': {
                    'rotate_to_storage': [i.get('id') for i in storage_items[:10]],
                    'consider_donating': [i.get('id') for i in rarely_worn[:5]],
                    'keep_accessible': [i.get('id') for i in active_items[:20]]
                },
                'message': f"Seasonal rotation complete: {len(active_items)} active items"
            }
            
            logger.info(f"[{self.name}] ✓ Seasonal rotation: {len(active_items)} active, {len(storage_items)} to storage")
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error in seasonal rotation: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'message': f"Error: {str(e)}"
            }
    
    def start_loop(self, check_interval: int = 60) -> None:
        """
        Start the task loop
        
        Args:
            check_interval: Seconds between checks
        """
        logger.info(f"[{self.name}] Starting task loop (check every {check_interval}s)")
        self.running = True
        
        try:
            while self.running:
                current_time = datetime.now()
                
                # Check each task
                for task in self.tasks:
                    if not task['enabled']:
                        continue
                    
                    # Check if it's time to run
                    if (current_time.hour == task['hour'] and 
                        current_time.minute == task['minute']):
                        
                        # Check if already run today
                        last_run = task.get('last_run')
                        if last_run:
                            last_run_date = datetime.fromisoformat(last_run).date()
                            if last_run_date == current_time.date():
                                continue  # Already run today
                        
                        # Execute task
                        logger.info(f"[{self.name}] Executing scheduled task: {task['name']}")
                        task['callback']()
                        task['last_run'] = current_time.isoformat()
                
                # Sleep until next check
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            logger.info(f"[{self.name}] Loop stopped by user")
            self.running = False
    
    def stop_loop(self) -> dict:
        """Stop the task loop"""
        logger.info(f"[{self.name}] Stopping task loop")
        self.running = False
        
        return {
            'success': True,
            'agent': self.name,
            'message': 'Task loop stopped'
        }
    
    def get_scheduled_tasks(self) -> dict:
        """Get list of scheduled tasks"""
        task_list = []
        for task in self.tasks:
            task_list.append({
                'name': task['name'],
                'time': task['time'],
                'enabled': task['enabled'],
                'last_run': task.get('last_run')
            })
        
        return {
            'success': True,
            'agent': self.name,
            'tasks': task_list,
            'message': f"Found {len(task_list)} scheduled tasks"
        }
    
    def get_agent_status(self) -> dict:
        """Get agent status"""
        return {
            'name': self.name,
            'status': 'active' if self.running else 'idle',
            'capabilities': [
                'daily_scheduling',
                'morning_routine',
                'seasonal_rotation',
                'task_management',
                'long_running_operations'
            ],
            'scheduled_tasks': len(self.tasks),
            'loop_running': self.running,
            'ready': True
        }


# Test
if __name__ == "__main__":
    agent = LoopAgent()
    print(agent.get_agent_status())
    
    # Test scheduling
    def mock_callback():
        print("Morning outfit generated!")
    
    result = agent.schedule_daily_outfit("07:00", mock_callback)
    print(f"Schedule result: {result}")