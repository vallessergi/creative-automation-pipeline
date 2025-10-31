import re
from typing import Dict, List, Tuple
from pathlib import Path
from loguru import logger
from PIL import Image

class ContentModerator:
    def __init__(self):
        # Discriminatory terms and phrases
        self.discriminatory_terms = [
            # Age discrimination
            'too old', 'too young', 'elderly', 'seniors only', 'young people only',
            # Gender discrimination  
            'men only', 'women only', 'boys only', 'girls only', 'male only', 'female only',
            # Race/ethnicity
            'whites only', 'blacks only', 'asians only', 'latinos only', 'hispanics only',
            # Religion
            'christians only', 'muslims only', 'jews only', 'religious only',
            # Sexual orientation
            'straight only', 'gay only', 'heterosexual only',
            # Disability
            'healthy only', 'disabled only', 'handicapped only',
            # General discriminatory
            'discrimination', 'segregation', 'exclude', 'ban', 'prohibit based on'
        ]
        
        # Illegal/harmful content
        self.illegal_terms = [
            # Violence
            'violence', 'harm', 'hurt', 'kill', 'attack', 'weapon', 'gun', 'knife',
            # Drugs/substances
            'drugs', 'cocaine', 'heroin', 'marijuana', 'cannabis', 'illegal substances',
            # Hate speech
            'hate', 'racist', 'sexist', 'homophobic', 'transphobic', 'nazi', 'supremacy',
            # Adult content
            'pornography', 'explicit', 'adult content', 'sexual content',
            # Scams/fraud
            'get rich quick', 'guaranteed money', 'free money', 'pyramid scheme', 'scam',
            # Medical claims
            'cure cancer', 'miracle cure', 'guaranteed results', 'medical breakthrough',
            # False claims
            'guaranteed', 'instant results', '100% effective', 'miracle', 'magic'
        ]

    def _check_campaign_message(self, campaign_message: str) -> Tuple[bool, str, List[str]]:
        """
        Check campaign message for compliance (private method)
        Returns: (is_compliant, failure_reason, flagged_terms)
        """
        message_lower = campaign_message.lower()
        flagged_terms = []
        
        # Check for discriminatory content
        for term in self.discriminatory_terms:
            if term in message_lower:
                flagged_terms.append(term)
        
        if flagged_terms:
            reason = f"Uncompliant message due to discriminatory content: {', '.join(flagged_terms)}"
            logger.warning(f"Campaign message failed discrimination check: {reason}")
            return False, reason, flagged_terms
        
        # Check for illegal content
        flagged_terms = []
        for term in self.illegal_terms:
            if term in message_lower:
                flagged_terms.append(term)
        
        if flagged_terms:
            reason = f"Uncompliant message due to inappropriate content: {', '.join(flagged_terms)}"
            logger.warning(f"Campaign message failed content check: {reason}")
            return False, reason, flagged_terms
        
        # Check for excessive promotional language (basic check)
        promotional_words = ['guaranteed', 'instant', 'miracle', 'magic', '100%', 'free money']
        flagged_promotional = [word for word in promotional_words if word in message_lower]
        
        if len(flagged_promotional) > 2:  # Allow some promotional language but not excessive
            reason = f"Uncompliant message due to excessive promotional claims: {', '.join(flagged_promotional)}"
            logger.warning(f"Campaign message failed promotional check: {reason}")
            return False, reason, flagged_promotional
        
        logger.info("Campaign message passed content moderation checks")
        return True, "", []
    
    def _check_target_audience(self, target_audience: str) -> Tuple[bool, str, List[str]]:
        """
        Check target audience for discriminatory targeting (private method)
        Returns: (is_compliant, failure_reason, flagged_terms)
        """
        audience_lower = target_audience.lower()
        flagged_terms = []
        
        # Check for discriminatory targeting
        discriminatory_targeting = [
            'exclude', 'only', 'ban', 'prohibit', 'not allowed', 'forbidden',
            'whites only', 'blacks only', 'men only', 'women only', 'straight only'
        ]
        
        for term in discriminatory_targeting:
            if term in audience_lower and 'age' not in audience_lower:  # Allow age targeting
                flagged_terms.append(term)
        
        if flagged_terms:
            reason = f"Uncompliant targeting due to discriminatory audience selection: {', '.join(flagged_terms)}"
            logger.warning(f"Target audience failed compliance check: {reason}")
            return False, reason, flagged_terms
        
        logger.info("Target audience passed content moderation checks")
        return True, "", []
    
    def validate_campaign_content(self, campaign_brief: Dict) -> Tuple[bool, str]:
        """
        Validate entire campaign content for compliance (public method)
        Returns: (is_compliant, failure_reason)
        """
        # Check campaign message
        message_compliant, message_reason, _ = self._check_campaign_message(
            campaign_brief.get('campaign_message', '')
        )
        
        if not message_compliant:
            return False, message_reason
        
        # Check target audience
        audience_compliant, audience_reason, _ = self._check_target_audience(
            campaign_brief.get('target_audience', '')
        )
        
        if not audience_compliant:
            return False, audience_reason
        
        return True, "Content passed all compliance checks"
    
    def _get_dominant_color(self, image_path: str) -> str:
        """Get the dominant color of an image (private method)"""
        try:
            with Image.open(image_path) as img:
                # Get the color of the center pixel as representative of background
                width, height = img.size
                center_pixel = img.getpixel((width // 2, height // 2))
                
                # Handle both RGB and RGBA
                if len(center_pixel) >= 3:
                    r, g, b = center_pixel[:3]
                    
                    # Determine if it's predominantly red
                    if r > 200 and g < 100 and b < 100:  # Strong red
                        return "red"
                    elif g > 200 and r < 100 and b < 100:  # Strong green
                        return "green"
                    elif b > 200 and r < 100 and g < 100:  # Strong blue
                        return "blue"
                    elif r > 200 and g > 200 and b < 100:  # Strong yellow
                        return "yellow"
                    else:
                        return "other"
                        
        except Exception as e:
            logger.error(f"Failed to analyze image color: {str(e)}")
            return "unknown"
    
    def check_brand_compliance(self, campaign_id: str) -> Tuple[bool, str]:
        """
        Check generated campaign images for brand compliance
        Returns: (is_compliant, failure_reason)
        """
        try:
            output_dir = Path("output") / campaign_id
            
            if not output_dir.exists():
                return True, "No images to check"
            
            red_images = []
            
            # Check all generated images in campaign
            for product_dir in output_dir.iterdir():
                if product_dir.is_dir():
                    for image_file in product_dir.glob("*.jpg"):
                        color = self._get_dominant_color(str(image_file))
                        if color == "red":
                            red_images.append(str(image_file.relative_to(output_dir)))
            
            if red_images:
                reason = f"Brand compliance failure: Red background detected in images: {', '.join(red_images)}"
                logger.warning(f"Campaign {campaign_id} failed brand compliance: {reason}")
                return False, reason
            
            logger.info(f"Campaign {campaign_id} passed brand compliance checks")
            return True, "Brand compliance check passed - no red backgrounds detected"
            
        except Exception as e:
            logger.error(f"Brand compliance check failed for campaign {campaign_id}: {str(e)}")
            return False, f"Brand compliance check error: {str(e)}"