import re
import os
import json
from typing import Dict, List, Tuple
from loguru import logger
from groq import Groq

class ContentModerator:
    def __init__(self, groq_api_key: str = None):
        """Initialize the AI-powered content moderator using Groq"""
 

        self.groq_client = Groq(api_key=groq_api_key)
        logger.info("Groq AI client initialized successfully")
        
        self.model = "llama-3.1-8b-instant"
        
        self.moderation_prompt = """You are a content moderation AI for advertising campaigns. Analyze the following content and determine if it violates any policies.

        Check for:
        1. Discriminatory content (age, gender, race, religion, sexual orientation, disability discrimination)
        2. Illegal content (violence, drugs, hate speech, adult content, scams)
        3. False or misleading claims (medical claims, guaranteed results, miracle cures)
        4. Excessive promotional language that could be considered misleading

        Content to analyze: "{content}"

        Respond with a JSON object in this exact format:
        {{
            "is_compliant": true/false,
            "violations": ["list of specific violations found"],
            "reason": "brief explanation of why content was flagged or approved"
        }}

        Be strict but fair. Only flag content that clearly violates policies."""

    def _analyze_content_with_ai(self, content: str, content_type: str) -> Tuple[bool, str, List[str]]:
        """
        Analyze content using Groq AI for compliance
        Returns: (is_compliant, failure_reason, flagged_violations)
        """

        prompt = self.moderation_prompt.format(content=content)
        
        response = self.groq_client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # Low temperature for consistent results
            max_tokens=500
        )
        
        ai_response = response.choices[0].message.content.strip()
        logger.debug(f"AI moderation response: {ai_response}")
        
        result = json.loads(ai_response)
        is_compliant = result.get("is_compliant", True)
        violations = result.get("violations", [])
        reason = result.get("reason", "")
        
        if not is_compliant:
            logger.warning(f"Policy violations in {content_type}: {reason}")
            return False, f"{reason}", violations
        else:
            logger.info(f"AI approved {content_type}: {reason}")
            return True, "", []

    def _check_campaign_message(self, campaign_message: str) -> Tuple[bool, str, List[str]]:
        """
        Check campaign message for compliance using AI (private method)
        Returns: (is_compliant, failure_reason, flagged_violations)
        """
        return self._analyze_content_with_ai(campaign_message, "campaign message")
    
    def _check_target_audience(self, target_audience: str) -> Tuple[bool, str, List[str]]:
        """
        Check target audience for discriminatory targeting using AI (private method)
        Returns: (is_compliant, failure_reason, flagged_violations)
        """
        return self._analyze_content_with_ai(target_audience, "target audience")
    
    def validate_campaign_content(self, campaign_brief: Dict) -> Tuple[bool, str]:
        """
        Validate entire campaign content for compliance (public method)
        Returns: (is_compliant, failure_reason)
        """

        message_compliant, message_reason, _ = self._check_campaign_message(
            campaign_brief.get('campaign_message', '')
        )
        
        if not message_compliant:
            return False, message_reason
        
        audience_compliant, audience_reason, _ = self._check_target_audience(
            campaign_brief.get('target_audience', '')
        )
        
        if not audience_compliant:
            return False, audience_reason
        
        return True, "Content passed all compliance checks"
    