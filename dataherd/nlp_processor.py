#!/usr/bin/env python3
"""
DataHerd NLP Processor

This module handles natural language processing for data cleaning rules,
converting plain English descriptions into executable data processing logic.
"""

import re
import json
import logging
from typing import Dict, Any, Optional, List
from enum import Enum
from dataclasses import dataclass
import openai
from config.config import get_openai_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RuleType(Enum):
    """Enumeration of rule types"""
    VALIDATION = "validation"
    STANDARDIZATION = "standardization"
    CLEANING = "cleaning"
    ESTIMATION = "estimation"


@dataclass
class ParsedRule:
    """Structured representation of a parsed rule"""
    rule_type: RuleType
    field: str
    condition: str
    action: str
    parameters: Dict[str, Any]
    confidence: float
    description: str
    client_context: Optional[str] = None


class NLPProcessor:
    """Natural Language Processor for data cleaning rules"""
    
    def __init__(self):
        """Initialize the NLP processor"""
        self.openai_client = get_openai_client()
        self.pattern_rules = self._initialize_pattern_rules()
    
    def _initialize_pattern_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize pattern-based rule parsing for fallback"""
        return {
            'weight_validation': {
                'patterns': [
                    r'weight\s+(?:below|under|less\s+than)\s+(\d+)',
                    r'weight\s+(?:above|over|more\s+than)\s+(\d+)',
                    r'weight\s+between\s+(\d+)\s+and\s+(\d+)'
                ],
                'rule_type': RuleType.VALIDATION,
                'field': 'weight'
            },
            'breed_standardization': {
                'patterns': [
                    r'standardize\s+breed\s+names',
                    r'capitalize\s+breed\s+names',
                    r'breed\s+standardization'
                ],
                'rule_type': RuleType.STANDARDIZATION,
                'field': 'breed'
            },
            'date_validation': {
                'patterns': [
                    r'birth\s+date\s+validation',
                    r'date\s+range\s+(\d{4})\s*-\s*(\d{4})'
                ],
                'rule_type': RuleType.VALIDATION,
                'field': 'birth_date'
            }
        }
    
    def parse_natural_language_rule(self, rule_text: str, client_context: str = "") -> ParsedRule:
        """
        Parse natural language rule into structured format
        
        Args:
            rule_text: Natural language description of the rule
            client_context: Client context (e.g., "Elanco")
            
        Returns:
            ParsedRule object with structured rule information
        """
        try:
            # Try OpenAI API first
            if self.openai_client:
                return self._parse_with_openai(rule_text, client_context)
            else:
                # Fallback to pattern matching
                return self._parse_with_patterns(rule_text, client_context)
        except Exception as e:
            logger.error(f"Error parsing rule: {e}")
            # Return a basic fallback rule
            return self._create_fallback_rule(rule_text, client_context)
    
    def _parse_with_openai(self, rule_text: str, client_context: str) -> ParsedRule:
        """Parse rule using OpenAI API"""
        try:
            prompt = f"""
            Parse the following natural language data cleaning rule for cattle data:
            
            Rule: "{rule_text}"
            Client Context: "{client_context}"
            
            Return a JSON object with the following structure:
            {{
                "rule_type": "validation|standardization|cleaning|estimation",
                "field": "field_name",
                "condition": "python_condition",
                "action": "action_to_take",
                "parameters": {{"param1": "value1"}},
                "confidence": 0.95,
                "description": "rule_description"
            }}
            
            Examples:
            - "Flag cattle with weight below 400 pounds" → validation rule
            - "Standardize breed names to proper case" → standardization rule
            - "Remove records with missing birth dates" → cleaning rule
            """
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            parsed_data = json.loads(content)
            
            return ParsedRule(
                rule_type=RuleType(parsed_data['rule_type']),
                field=parsed_data['field'],
                condition=parsed_data['condition'],
                action=parsed_data['action'],
                parameters=parsed_data['parameters'],
                confidence=parsed_data['confidence'],
                description=parsed_data['description'],
                client_context=client_context
            )
            
        except Exception as e:
            logger.error(f"OpenAI parsing failed: {e}")
            raise
    
    def _parse_with_patterns(self, rule_text: str, client_context: str) -> ParsedRule:
        """Parse rule using pattern matching (fallback)"""
        rule_text_lower = rule_text.lower()
        
        # Check for weight validation patterns
        for pattern in self.pattern_rules['weight_validation']['patterns']:
            match = re.search(pattern, rule_text_lower)
            if match:
                return ParsedRule(
                    rule_type=RuleType.VALIDATION,
                    field='weight',
                    condition=f"weight < {match.group(1)}" if 'below' in pattern else f"weight > {match.group(1)}",
                    action='flag_as_error',
                    parameters={'threshold': int(match.group(1))},
                    confidence=0.8,
                    description=f"Weight validation rule: {rule_text}",
                    client_context=client_context
                )
        
        # Check for breed standardization patterns
        for pattern in self.pattern_rules['breed_standardization']['patterns']:
            if re.search(pattern, rule_text_lower):
                return ParsedRule(
                    rule_type=RuleType.STANDARDIZATION,
                    field='breed',
                    condition='breed is not None',
                    action='capitalize_breed',
                    parameters={},
                    confidence=0.9,
                    description=f"Breed standardization rule: {rule_text}",
                    client_context=client_context
                )
        
        # Default fallback
        return self._create_fallback_rule(rule_text, client_context)
    
    def _create_fallback_rule(self, rule_text: str, client_context: str) -> ParsedRule:
        """Create a basic fallback rule when parsing fails"""
        return ParsedRule(
            rule_type=RuleType.VALIDATION,
            field='general',
            condition='True',
            action='flag_for_review',
            parameters={'original_rule': rule_text},
            confidence=0.5,
            description=f"Fallback rule for: {rule_text}",
            client_context=client_context
        )
    
    def validate_rule(self, parsed_rule: ParsedRule) -> bool:
        """Validate a parsed rule for correctness"""
        try:
            # Basic validation checks
            if not parsed_rule.field or not parsed_rule.condition:
                return False
            
            if parsed_rule.confidence < 0 or parsed_rule.confidence > 1:
                return False
            
            # Validate rule type
            if parsed_rule.rule_type not in RuleType:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Rule validation failed: {e}")
            return False
    
    def get_rule_suggestions(self, data_sample: Dict[str, Any], client_context: str = "") -> List[str]:
        """Generate rule suggestions based on data sample"""
        suggestions = []
        
        # Analyze data and suggest common rules
        if 'weight' in data_sample:
            suggestions.append("Flag cattle with weight below 400 pounds")
            suggestions.append("Flag cattle with weight above 1500 pounds")
        
        if 'breed' in data_sample:
            suggestions.append("Standardize breed names to proper case")
        
        if 'birth_date' in data_sample:
            suggestions.append("Validate birth dates are within reasonable range")
        
        return suggestions 