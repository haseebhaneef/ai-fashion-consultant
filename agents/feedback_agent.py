"""Feedback Agent - Collects and processes user feedback"""

import logging
import google.generativeai as genai
import json
from datetime import datetime
from config.settings import GEMINI_API_KEY, GEMINI_MODEL
from config.prompts import FEEDBACK_SYSTEM_PROMPT

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

genai.configure(api_key=GEMINI_API_KEY)

class FeedbackAgent:
    """
    Collects user feedback on outfits
    Extracts insights for personalization
    """
    
    def __init__(self):
        self.name = "FeedbackAgent"
        self.model = genai.GenerativeModel(GEMINI_MODEL)
        logger.info(f"✓ {self.name} initialized")
    
    def process_feedback(self, feedback_text: str, outfit: dict, context: dict = None) -> dict:
        """
        Process natural language feedback
        
        Args:
            feedback_text: User's feedback
            outfit: The outfit being reviewed
            context: Additional context (weather, occasion, etc.)
            
        Returns:
            dict: Structured feedback insights
        """
        logger.info(f"[{self.name}] Processing feedback: '{feedback_text[:50]}...'")
        
        try:
            # Build analysis prompt
            prompt = f"""{FEEDBACK_SYSTEM_PROMPT}

User Feedback: "{feedback_text}"

Outfit Details:
{json.dumps(outfit, indent=2)}

Context: {json.dumps(context or {}, indent=2)}

Analyze this feedback and extract structured insights about the user's preferences.
Return JSON with feedback_type, specific_elements, and preference_updates."""

            # Generate analysis
            response = self.model.generate_content(prompt)
            insights = self._parse_feedback_response(response.text)
            
            # Determine sentiment
            sentiment = self._determine_sentiment(feedback_text, insights)
            
            result = {
                'success': True,
                'agent': self.name,
                'feedback_text': feedback_text,
                'sentiment': sentiment,
                'insights': insights,
                'timestamp': datetime.now().isoformat(),
                'outfit_id': context.get('outfit_id') if context else None,
                'message': 'Feedback processed successfully'
            }
            
            logger.info(f"[{self.name}] ✓ Feedback processed: {sentiment} sentiment")
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error processing feedback: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'message': f"Error: {str(e)}"
            }
    
    def collect_rating(self, outfit_id: int, rating: int, comments: str = "") -> dict:
        """
        Collect simple rating feedback
        
        Args:
            outfit_id: Outfit identifier
            rating: Rating 1-5
            comments: Optional text comments
            
        Returns:
            dict: Feedback record
        """
        logger.info(f"[{self.name}] Collecting rating: {rating}/5 for outfit #{outfit_id}")
        
        # Map rating to sentiment
        if rating >= 4:
            sentiment = "positive"
        elif rating >= 3:
            sentiment = "neutral"
        else:
            sentiment = "negative"
        
        feedback = {
            'success': True,
            'agent': self.name,
            'outfit_id': outfit_id,
            'rating': rating,
            'sentiment': sentiment,
            'comments': comments,
            'timestamp': datetime.now().isoformat(),
            'message': f"Rating {rating}/5 recorded"
        }
        
        logger.info(f"[{self.name}] ✓ Rating recorded: {rating}/5")
        return feedback
    
    def analyze_feedback_trends(self, feedback_history: list) -> dict:
        """
        Analyze patterns in feedback history
        
        Args:
            feedback_history: List of past feedback records
            
        Returns:
            dict: Trend analysis
        """
        logger.info(f"[{self.name}] Analyzing {len(feedback_history)} feedback records")
        
        if not feedback_history:
            return {
                'success': True,
                'agent': self.name,
                'trends': {},
                'message': 'No feedback history to analyze'
            }
        
        # Count sentiments
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        total_ratings = []
        
        for fb in feedback_history:
            sentiment = fb.get('sentiment', 'neutral')
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
            
            if 'rating' in fb:
                total_ratings.append(fb['rating'])
        
        # Calculate trends
        total = len(feedback_history)
        trends = {
            'total_feedbacks': total,
            'positive_rate': sentiment_counts['positive'] / total if total > 0 else 0,
            'negative_rate': sentiment_counts['negative'] / total if total > 0 else 0,
            'average_rating': sum(total_ratings) / len(total_ratings) if total_ratings else 0,
            'sentiment_distribution': sentiment_counts,
            'satisfaction_score': sentiment_counts['positive'] / total if total > 0 else 0
        }
        
        # Generate insights
        if trends['positive_rate'] >= 0.7:
            insight = "User is very satisfied with recommendations"
        elif trends['positive_rate'] >= 0.5:
            insight = "User is moderately satisfied - room for improvement"
        else:
            insight = "User satisfaction is low - significant adjustments needed"
        
        result = {
            'success': True,
            'agent': self.name,
            'trends': trends,
            'insight': insight,
            'message': 'Trend analysis complete'
        }
        
        logger.info(f"[{self.name}] ✓ Trends: {trends['positive_rate']:.0%} positive rate")
        return result
    
    def _parse_feedback_response(self, response_text: str) -> dict:
        """Parse structured insights from AI response"""
        try:
            text = response_text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            insights = json.loads(text.strip())
            return insights
            
        except json.JSONDecodeError:
            logger.warning("Failed to parse feedback JSON, using text fallback")
            return {
                'feedback_type': 'neutral',
                'specific_elements': {},
                'preference_updates': {},
                'raw_text': response_text
            }
    
    def _determine_sentiment(self, feedback_text: str, insights: dict) -> str:
        """Determine sentiment from feedback"""
        # Use insights if available
        feedback_type = insights.get('feedback_type', 'neutral')
        if feedback_type in ['positive', 'negative', 'neutral']:
            return feedback_type
        
        # Fallback: simple keyword matching
        positive_words = ['love', 'great', 'perfect', 'amazing', 'good', 'like', 'comfortable']
        negative_words = ['hate', 'bad', 'uncomfortable', 'dislike', 'wrong', 'ugly', 'weird']
        
        text_lower = feedback_text.lower()
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return 'positive'
        elif neg_count > pos_count:
            return 'negative'
        else:
            return 'neutral'
    
    def get_agent_status(self) -> dict:
        """Get agent status"""
        return {
            'name': self.name,
            'status': 'active',
            'capabilities': [
                'feedback_processing',
                'sentiment_analysis',
                'insight_extraction',
                'rating_collection',
                'trend_analysis'
            ],
            'model': GEMINI_MODEL,
            'ready': True
        }


# Test
if __name__ == "__main__":
    agent = FeedbackAgent()
    print(agent.get_agent_status())
    
    # Test feedback
    feedback = agent.collect_rating(1, 5, "Loved this outfit!")
    print(f"Feedback: {feedback}")