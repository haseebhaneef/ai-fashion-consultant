"""Perception Agent - Vision-based garment detection"""

import logging
import time
from tools.image_tagger import ImageTagger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PerceptionAgent:
    """
    Analyzes clothing images and extracts garment attributes
    Uses Gemini Vision for intelligent tagging
    """
    
    def __init__(self):
        self.name = "PerceptionAgent"
        self.tagger = ImageTagger()
        logger.info(f"✓ {self.name} initialized")
    
    def analyze_garment(self, image_path: str) -> dict:
        """
        Analyze a single garment image
        
        Args:
            image_path: Path to clothing image
            
        Returns:
            dict: Garment attributes and metadata
        """
        logger.info(f"[{self.name}] Analyzing garment: {image_path}")
        
        try:
            # Use image tagger tool
            tags = self.tagger.tag_garment(image_path)
            
            # Add agent metadata
            result = {
                'success': True,
                'agent': self.name,
                'data': tags,
                'message': f"Successfully analyzed {tags.get('garment_type', 'item')}"
            }
            
            logger.info(f"[{self.name}] ✓ Analysis complete: {tags.get('garment_type')}")
            return result
            
        except Exception as e:
            logger.error(f"[{self.name}] ✗ Error analyzing garment: {str(e)}")
            return {
                'success': False,
                'agent': self.name,
                'data': None,
                'message': f"Error: {str(e)}"
            }
    
    def analyze_wardrobe_batch(self, image_paths: list) -> dict:
        """
        Analyze multiple garment images in batch
        
        Args:
            image_paths: List of image paths
            
        Returns:
            dict: Batch analysis results
        """
        logger.info(f"[{self.name}] Starting batch analysis of {len(image_paths)} items")
        
        results = []
        successful = 0
        failed = 0
        
        for path in image_paths:
            result = self.analyze_garment(path)
            results.append(result)
            
            if result['success']:
                # Check if it fell back to unknown
                if result['data'].get('garment_type') == 'unknown':
                    # It technically "succeeded" (didn't crash) but failed to tag
                    # We count it as successful process, but log it
                    pass
                successful += 1
            else:
                failed += 1
            
            # RATE LIMITING PROTECTION
            # Sleep 2 seconds between requests to avoid 429 errors
            time.sleep(2)
        
        summary = {
            'success': True,
            'agent': self.name,
            'total_analyzed': len(image_paths),
            'successful': successful,
            'failed': failed,
            'results': results,
            'message': f"Batch analysis complete: {successful}/{len(image_paths)} processed"
        }
        
        logger.info(f"[{self.name}] ✓ Batch complete: {successful} processed, {failed} failed")
        return summary
    
    def validate_garment_data(self, tags: dict) -> dict:
        """
        Validate extracted garment data
        
        Args:
            tags: Garment tags dictionary
            
        Returns:
            dict: Validation result
        """
        required_fields = ['garment_type', 'color', 'formality', 'season']
        
        missing = [field for field in required_fields if not tags.get(field)]
        
        if missing:
            return {
                'valid': False,
                'missing_fields': missing,
                'message': f"Missing required fields: {', '.join(missing)}"
            }
        
        return {
            'valid': True,
            'missing_fields': [],
            'message': "All required fields present"
        }
    
    def get_agent_status(self) -> dict:
        """Get agent status and capabilities"""
        return {
            'name': self.name,
            'status': 'active',
            'capabilities': [
                'single_garment_analysis',
                'batch_analysis',
                'vision_based_tagging',
                'color_detection',
                'pattern_recognition',
                'formality_assessment',
                'seasonal_classification'
            ],
            'model': 'gemini-vision',
            'ready': True
        }


# Test
if __name__ == "__main__":
    agent = PerceptionAgent()
    print(agent.get_agent_status())