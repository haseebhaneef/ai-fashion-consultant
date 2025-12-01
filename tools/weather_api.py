"""Weather API integration"""

import requests
import logging
from config.settings import WEATHER_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherAPI:
    """Fetch weather data for outfit planning"""
    
    def __init__(self, api_key: str = WEATHER_API_KEY):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
    
    def get_weather(self, city: str = "New York") -> dict:
        """
        Get current weather for a city
        
        Args:
            city: City name
            
        Returns:
            dict: Weather data
        """
        if not self.api_key or self.api_key == "your_weather_api_key_here":
            logger.warning("No Weather API key configured, using mock data")
            return self._mock_weather()
        
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'imperial'  # Fahrenheit
            }
            
            response = requests.get(self.base_url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            weather_info = {
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'condition': data['weather'][0]['main'],
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed'],
                'city': city
            }
            
            logger.info(f"✓ Weather for {city}: {weather_info['temperature']}°F, {weather_info['condition']}")
            return weather_info
            
        except Exception as e:
            logger.error(f"✗ Weather API error: {str(e)}")
            return self._mock_weather()
    
    def _mock_weather(self) -> dict:
        """Return mock weather data for testing"""
        return {
            'temperature': 72,
            'feels_like': 70,
            'condition': 'Clear',
            'description': 'clear sky',
            'humidity': 45,
            'wind_speed': 5,
            'city': 'Demo City'
        }
    
    def get_outfit_suggestion(self, weather: dict) -> str:
        """Get weather-based outfit suggestions"""
        temp = weather['temperature']
        condition = weather['condition'].lower()
        
        if temp < 40:
            return "cold_weather_heavy"
        elif temp < 60:
            return "cool_weather_layers"
        elif temp < 75:
            return "mild_weather_comfortable"
        elif temp < 85:
            return "warm_weather_light"
        else:
            return "hot_weather_minimal"


# Test
if __name__ == "__main__":
    api = WeatherAPI()
    weather = api.get_weather("London")
    print(f"Weather: {weather}")
    suggestion = api.get_outfit_suggestion(weather)
    print(f"Suggestion: {suggestion}")