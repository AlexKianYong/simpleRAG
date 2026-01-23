"""
Guardrails module for detecting and filtering adversarial prompts.
Implements detection mechanisms for:
- Prompt injection attacks
- Jailbreak attempts
- Out-of-domain questions
- Malicious content
"""

import re
from typing import Tuple


class AdversarialGuardrails:
    """Detects and filters adversarial prompts."""
    
    def __init__(self):
        """Initialize guardrails with common malicious patterns."""
        # Patterns for prompt injection attempts
        self.injection_patterns = [
            r'ignore.*instruction',
            r'forget.*your.*instruction',
            r'system.*prompt',
            r'override.*instruction',
            r'bypass.*security',
            r'show.*me.*your.*prompt',
            r'what.*is.*your.*system.*prompt',
        ]
        
        # Patterns for jailbreak attempts
        self.jailbreak_patterns = [
            r'pretend.*you.*are',
            r'roleplay.*as',
            r'imagine.*you.*are',
            r'act.*as.*if',
        ]
        
        # Out-of-domain keywords
        self.out_of_domain_keywords = [
            'hack', 'malware', 'exploit', 'crack', 'password',
            'bitcoin', 'crypto', 'medical', 'legal', 'financial advice',
            'bomb', 'weapon', 'drug', 'illegal'
        ]
        
        # TNGD-related keywords (legitimate domain)
        self.legitimate_keywords = [
            'touch n go', 'tng', 'ewallet', 'card', 'payment',
            'transaction', 'balance', 'reload', 'toll', 'fee',
            'account', 'help', 'problem', 'issue', 'how to'
        ]
    
    def is_adversarial(self, question: str) -> Tuple[bool, str]:
        """
        Check if a question contains adversarial content.
        
        Args:
            question: The user's question
            
        Returns:
            Tuple of (is_adversarial: bool, reason: str)
        """
        question_lower = question.lower()
        
        # Check for prompt injection patterns
        for pattern in self.injection_patterns:
            if re.search(pattern, question_lower, re.IGNORECASE):
                return True, "Prompt injection detected"
        
        # Check for jailbreak patterns
        for pattern in self.jailbreak_patterns:
            if re.search(pattern, question_lower, re.IGNORECASE):
                return True, "Jailbreak attempt detected"
        
        # Check for out-of-domain harmful keywords
        for keyword in self.out_of_domain_keywords:
            if keyword in question_lower:
                return True, f"Harmful content detected: {keyword}"
        
        # Check if question is about TNGD at all
        has_legitimate_keyword = any(
            kw in question_lower for kw in self.legitimate_keywords
        )
        
        # If question doesn't mention TNGD or related terms, it might be out of scope
        if not has_legitimate_keyword and len(question) > 10:
            # Allow very short questions or those with explicit markers
            if not any(marker in question_lower for marker in ['tngd', 'touch', 'go', 'ewallet']):
                # This is a heuristic - we'll return False to let the semantic search decide
                # but you can make this stricter
                pass
        
        return False, ""
    
    def is_spam_or_gibberish(self, question: str) -> Tuple[bool, str]:
        """
        Check if question is spam or gibberish.
        
        Args:
            question: The user's question
            
        Returns:
            Tuple of (is_spam: bool, reason: str)
        """
        # Too short
        if len(question.strip()) <= 3:
            return True, "Question is too short"
        
        # All caps or mostly special characters
        if len(question) > 10:
            special_char_ratio = sum(1 for c in question if not c.isalnum() and not c.isspace()) / len(question)
            if special_char_ratio > 0.5:
                return True, "Too many special characters"
        
        # Repeated characters
        if re.search(r'(.)\1{4,}', question):
            return True, "Repeated characters detected"
        
        return False, ""
    
    def check_question(self, question: str) -> dict:
        """
        Perform comprehensive check on a question.
        
        Args:
            question: The user's question
            
        Returns:
            Dictionary with check results
        """
        # Check for adversarial content
        is_adv, adv_reason = self.is_adversarial(question)
        if is_adv:
            return {
                'is_blocked': True,
                'reason': adv_reason,
                'category': 'adversarial'
            }
        
        # Check for spam/gibberish
        is_spam, spam_reason = self.is_spam_or_gibberish(question)
        if is_spam:
            return {
                'is_blocked': True,
                'reason': spam_reason,
                'category': 'spam'
            }
        
        return {
            'is_blocked': False,
            'reason': '',
            'category': 'legitimate'
        }
