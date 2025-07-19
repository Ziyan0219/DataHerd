"""
Natural Language Processing module for DataHerd
Converts natural language rules into executable data cleaning operations
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import openai
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RuleType(Enum):
    VALIDATION = "validation"
    STANDARDIZATION = "standardization"
    CLEANING = "cleaning"
    ESTIMATION = "estimation"

@dataclass
class ParsedRule:
    """Represents a parsed natural language rule"""
    rule_type: RuleType
    field: str
    condition: str
    action: str
    parameters: Dict[str, Any]
    confidence: float
    description: str

class NLPProcessor:
    """Natural Language Processor for data cleaning rules"""
    
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        )
        
        # Common patterns for cattle data
        self.cattle_patterns = {
            'weight': {
                'typical_range': (400, 1500),
                'units': ['lbs', 'pounds', 'kg', 'kilograms'],
                'common_errors': ['missing_digit', 'decimal_error', 'unit_confusion']
            },
            'breed': {
                'common_breeds': ['Angus', 'Hereford', 'Holstein', 'Charolais', 'Simmental', 'Limousin'],
                'standardization': 'proper_case',
                'common_errors': ['case_mismatch', 'abbreviations', 'misspellings']
            },
            'birth_date': {
                'format': 'YYYY-MM-DD',
                'reasonable_range': (-3, 0),  # years from current date
                'common_errors': ['invalid_format', 'future_date', 'unrealistic_age']
            },
            'lot_id': {
                'format': 'alphanumeric',
                'common_errors': ['duplicates', 'missing_values', 'invalid_characters']
            }
        }
    
    def parse_natural_language_rule(self, rule_text: str, client_context: str = "") -> List[ParsedRule]:
        """
        Parse natural language rule into structured format
        
        Args:
            rule_text: Natural language description of the rule
            client_context: Additional context about the client (e.g., "Elanco")
            
        Returns:
            List of ParsedRule objects
        """
        try:
            # Create system prompt with cattle data context
            system_prompt = self._create_system_prompt()
            
            # Create user prompt with rule and context
            user_prompt = self._create_user_prompt(rule_text, client_context)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            # Parse the response
            parsed_rules = self._parse_api_response(response.choices[0].message.content)
            
            logger.info(f"Successfully parsed {len(parsed_rules)} rules from: {rule_text[:100]}...")
            return parsed_rules
            
        except Exception as e:
            logger.error(f"Error parsing natural language rule: {str(e)}")
            # Fallback to pattern-based parsing
            return self._fallback_pattern_parsing(rule_text)
    
    def _create_system_prompt(self) -> str:
        """Create system prompt for OpenAI API"""
        return """You are an expert data cleaning specialist for cattle lot management systems. 
        Your task is to convert natural language data cleaning rules into structured JSON format.
        
        Context: You're working with cattle data that typically includes:
        - lot_id: Unique identifier for each animal
        - weight: Animal weight in pounds (typical range 400-1500 lbs)
        - breed: Cattle breed (Angus, Hereford, Holstein, etc.)
        - birth_date: Date of birth in YYYY-MM-DD format
        - Other fields like health_status, feed_type, etc.
        
        Common data quality issues:
        - Weight errors: missing digits, decimal point errors, unrealistic values
        - Breed standardization: case mismatches, abbreviations, misspellings
        - Date validation: invalid formats, future dates, unrealistic ages
        - Duplicate records: same lot_id appearing multiple times
        - Missing values: null or empty critical fields
        
        For each rule, return a JSON array with objects containing:
        {
            "rule_type": "validation|standardization|cleaning|estimation",
            "field": "field_name",
            "condition": "when to apply this rule",
            "action": "what action to take",
            "parameters": {"key": "value pairs for rule parameters"},
            "confidence": 0.0-1.0,
            "description": "human readable description"
        }
        
        Be specific and actionable. Focus on cattle industry best practices."""
    
    def _create_user_prompt(self, rule_text: str, client_context: str) -> str:
        """Create user prompt with rule and context"""
        prompt = f"Convert this data cleaning rule into structured JSON format:\n\nRule: {rule_text}"
        
        if client_context:
            prompt += f"\n\nClient Context: {client_context}"
            prompt += "\nConsider any client-specific requirements or data patterns."
        
        prompt += "\n\nReturn only the JSON array, no additional text."
        return prompt
    
    def _parse_api_response(self, response_text: str) -> List[ParsedRule]:
        """Parse OpenAI API response into ParsedRule objects"""
        try:
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON array found in response")
            
            json_data = json.loads(json_match.group())
            
            parsed_rules = []
            for rule_data in json_data:
                parsed_rule = ParsedRule(
                    rule_type=RuleType(rule_data.get('rule_type', 'validation')),
                    field=rule_data.get('field', ''),
                    condition=rule_data.get('condition', ''),
                    action=rule_data.get('action', ''),
                    parameters=rule_data.get('parameters', {}),
                    confidence=float(rule_data.get('confidence', 0.8)),
                    description=rule_data.get('description', '')
                )
                parsed_rules.append(parsed_rule)
            
            return parsed_rules
            
        except Exception as e:
            logger.error(f"Error parsing API response: {str(e)}")
            raise
    
    def _fallback_pattern_parsing(self, rule_text: str) -> List[ParsedRule]:
        """Fallback pattern-based parsing when API fails"""
        rules = []
        rule_text_lower = rule_text.lower()
        
        # Weight validation patterns
        if 'weight' in rule_text_lower:
            if any(word in rule_text_lower for word in ['flag', 'validate', 'check']):
                if 'below' in rule_text_lower or 'above' in rule_text_lower:
                    # Extract numbers
                    numbers = re.findall(r'\d+', rule_text)
                    if len(numbers) >= 2:
                        min_weight = int(numbers[0])
                        max_weight = int(numbers[1])
                        
                        rule = ParsedRule(
                            rule_type=RuleType.VALIDATION,
                            field='weight',
                            condition=f'weight < {min_weight} or weight > {max_weight}',
                            action='flag_as_error',
                            parameters={'min_weight': min_weight, 'max_weight': max_weight},
                            confidence=0.7,
                            description=f'Flag weights outside {min_weight}-{max_weight} lbs range'
                        )
                        rules.append(rule)
        
        # Breed standardization patterns
        if 'breed' in rule_text_lower and 'standard' in rule_text_lower:
            rule = ParsedRule(
                rule_type=RuleType.STANDARDIZATION,
                field='breed',
                condition='breed is not properly capitalized',
                action='standardize_capitalization',
                parameters={'format': 'proper_case'},
                confidence=0.8,
                description='Standardize breed names to proper capitalization'
            )
            rules.append(rule)
        
        # Date validation patterns
        if 'date' in rule_text_lower and ('valid' in rule_text_lower or 'format' in rule_text_lower):
            rule = ParsedRule(
                rule_type=RuleType.VALIDATION,
                field='birth_date',
                condition='date format is invalid or unrealistic',
                action='validate_date_format',
                parameters={'format': 'YYYY-MM-DD', 'max_age_years': 3},
                confidence=0.7,
                description='Validate birth date format and reasonable age range'
            )
            rules.append(rule)
        
        # Duplicate removal patterns
        if 'duplicate' in rule_text_lower:
            rule = ParsedRule(
                rule_type=RuleType.CLEANING,
                field='lot_id',
                condition='duplicate lot_id found',
                action='remove_duplicates',
                parameters={'keep': 'first', 'based_on': ['lot_id']},
                confidence=0.9,
                description='Remove duplicate entries based on lot ID'
            )
            rules.append(rule)
        
        if not rules:
            # Generic rule if no patterns match
            rule = ParsedRule(
                rule_type=RuleType.VALIDATION,
                field='unknown',
                condition='generic condition',
                action='manual_review',
                parameters={},
                confidence=0.3,
                description=f'Manual review required for: {rule_text[:100]}'
            )
            rules.append(rule)
        
        return rules
    
    def generate_executable_code(self, parsed_rule: ParsedRule) -> str:
        """
        Generate executable Python code from parsed rule
        
        Args:
            parsed_rule: ParsedRule object
            
        Returns:
            Python code string
        """
        if parsed_rule.rule_type == RuleType.VALIDATION:
            return self._generate_validation_code(parsed_rule)
        elif parsed_rule.rule_type == RuleType.STANDARDIZATION:
            return self._generate_standardization_code(parsed_rule)
        elif parsed_rule.rule_type == RuleType.CLEANING:
            return self._generate_cleaning_code(parsed_rule)
        elif parsed_rule.rule_type == RuleType.ESTIMATION:
            return self._generate_estimation_code(parsed_rule)
        else:
            return f"# Unknown rule type: {parsed_rule.rule_type}"
    
    def _generate_validation_code(self, rule: ParsedRule) -> str:
        """Generate validation code"""
        if rule.field == 'weight':
            min_weight = rule.parameters.get('min_weight', 400)
            max_weight = rule.parameters.get('max_weight', 1500)
            return f"""
def validate_weight(df):
    \"\"\"Validate weight values\"\"\"
    issues = []
    for idx, row in df.iterrows():
        weight = row.get('{rule.field}')
        if pd.isna(weight) or weight < {min_weight} or weight > {max_weight}:
            issues.append({{
                'row_id': idx,
                'field': '{rule.field}',
                'value': weight,
                'issue': 'Weight outside normal range ({min_weight}-{max_weight} lbs)',
                'confidence': {rule.confidence}
            }})
    return issues
"""
        elif rule.field == 'birth_date':
            return f"""
def validate_birth_date(df):
    \"\"\"Validate birth date values\"\"\"
    issues = []
    current_date = pd.Timestamp.now()
    max_age_years = {rule.parameters.get('max_age_years', 3)}
    
    for idx, row in df.iterrows():
        birth_date = row.get('{rule.field}')
        try:
            date_obj = pd.to_datetime(birth_date)
            age_years = (current_date - date_obj).days / 365.25
            
            if age_years < 0 or age_years > max_age_years:
                issues.append({{
                    'row_id': idx,
                    'field': '{rule.field}',
                    'value': birth_date,
                    'issue': f'Unrealistic age: {{age_years:.1f}} years',
                    'confidence': {rule.confidence}
                }})
        except:
            issues.append({{
                'row_id': idx,
                'field': '{rule.field}',
                'value': birth_date,
                'issue': 'Invalid date format',
                'confidence': {rule.confidence}
            }})
    return issues
"""
        else:
            return f"""
def validate_{rule.field}(df):
    \"\"\"Generic validation for {rule.field}\"\"\"
    issues = []
    for idx, row in df.iterrows():
        value = row.get('{rule.field}')
        if pd.isna(value) or value == '':
            issues.append({{
                'row_id': idx,
                'field': '{rule.field}',
                'value': value,
                'issue': 'Missing or empty value',
                'confidence': {rule.confidence}
            }})
    return issues
"""
    
    def _generate_standardization_code(self, rule: ParsedRule) -> str:
        """Generate standardization code"""
        if rule.field == 'breed':
            return f"""
def standardize_breed(df):
    \"\"\"Standardize breed names\"\"\"
    changes = []
    breed_mapping = {{
        'angus': 'Angus',
        'hereford': 'Hereford',
        'holstein': 'Holstein',
        'charolais': 'Charolais',
        'simmental': 'Simmental',
        'limousin': 'Limousin'
    }}
    
    for idx, row in df.iterrows():
        original_breed = row.get('{rule.field}')
        if pd.notna(original_breed):
            standardized = breed_mapping.get(original_breed.lower(), original_breed.title())
            if standardized != original_breed:
                changes.append({{
                    'row_id': idx,
                    'field': '{rule.field}',
                    'original': original_breed,
                    'suggested': standardized,
                    'reason': 'Breed name standardization',
                    'confidence': {rule.confidence}
                }})
    return changes
"""
        else:
            return f"""
def standardize_{rule.field}(df):
    \"\"\"Standardize {rule.field} values\"\"\"
    changes = []
    for idx, row in df.iterrows():
        original_value = row.get('{rule.field}')
        if pd.notna(original_value) and isinstance(original_value, str):
            standardized = original_value.strip().title()
            if standardized != original_value:
                changes.append({{
                    'row_id': idx,
                    'field': '{rule.field}',
                    'original': original_value,
                    'suggested': standardized,
                    'reason': 'Value standardization',
                    'confidence': {rule.confidence}
                }})
    return changes
"""
    
    def _generate_cleaning_code(self, rule: ParsedRule) -> str:
        """Generate cleaning code"""
        if 'duplicate' in rule.action.lower():
            return f"""
def remove_duplicates(df):
    \"\"\"Remove duplicate records\"\"\"
    changes = []
    based_on = {rule.parameters.get('based_on', ['lot_id'])}
    keep = '{rule.parameters.get('keep', 'first')}'
    
    duplicates = df.duplicated(subset=based_on, keep=keep)
    duplicate_indices = df[duplicates].index.tolist()
    
    for idx in duplicate_indices:
        changes.append({{
            'row_id': idx,
            'field': 'record',
            'original': 'duplicate_record',
            'suggested': 'remove',
            'reason': f'Duplicate based on {{", ".join(based_on)}}',
            'confidence': {rule.confidence}
        }})
    
    return changes
"""
        else:
            return f"""
def clean_{rule.field}(df):
    \"\"\"Clean {rule.field} values\"\"\"
    changes = []
    for idx, row in df.iterrows():
        value = row.get('{rule.field}')
        if pd.isna(value) or value == '':
            changes.append({{
                'row_id': idx,
                'field': '{rule.field}',
                'original': value,
                'suggested': 'MISSING',
                'reason': 'Missing value flagged for attention',
                'confidence': {rule.confidence}
            }})
    return changes
"""
    
    def _generate_estimation_code(self, rule: ParsedRule) -> str:
        """Generate estimation code"""
        return f"""
def estimate_{rule.field}(df):
    \"\"\"Estimate missing {rule.field} values\"\"\"
    changes = []
    
    # Simple estimation based on available data
    valid_values = df[df['{rule.field}'].notna()]['{rule.field}']
    if len(valid_values) > 0:
        estimated_value = valid_values.median()  # or mean, mode depending on field
        
        for idx, row in df.iterrows():
            if pd.isna(row.get('{rule.field}')):
                changes.append({{
                    'row_id': idx,
                    'field': '{rule.field}',
                    'original': None,
                    'suggested': estimated_value,
                    'reason': 'Estimated based on median of valid values',
                    'confidence': {rule.confidence}
                }})
    
    return changes
"""

    def explain_rule(self, parsed_rule: ParsedRule) -> Dict[str, Any]:
        """
        Generate human-readable explanation of what the rule does
        
        Args:
            parsed_rule: ParsedRule object
            
        Returns:
            Dictionary with explanation details
        """
        explanation = {
            'summary': parsed_rule.description,
            'rule_type': parsed_rule.rule_type.value,
            'field': parsed_rule.field,
            'what_it_does': '',
            'when_it_applies': parsed_rule.condition,
            'action_taken': parsed_rule.action,
            'parameters': parsed_rule.parameters,
            'confidence': parsed_rule.confidence,
            'examples': []
        }
        
        # Generate specific explanations based on rule type
        if parsed_rule.rule_type == RuleType.VALIDATION:
            explanation['what_it_does'] = f"Validates that {parsed_rule.field} values meet specified criteria"
            if parsed_rule.field == 'weight':
                min_w = parsed_rule.parameters.get('min_weight', 400)
                max_w = parsed_rule.parameters.get('max_weight', 1500)
                explanation['examples'] = [
                    f"✓ Weight of 850 lbs is valid (within {min_w}-{max_w} range)",
                    f"✗ Weight of 45 lbs is flagged (below {min_w} lbs minimum)",
                    f"✗ Weight of 2000 lbs is flagged (above {max_w} lbs maximum)"
                ]
        
        elif parsed_rule.rule_type == RuleType.STANDARDIZATION:
            explanation['what_it_does'] = f"Standardizes {parsed_rule.field} values to consistent format"
            if parsed_rule.field == 'breed':
                explanation['examples'] = [
                    "✓ 'angus' → 'Angus' (proper capitalization)",
                    "✓ 'HEREFORD' → 'Hereford' (proper capitalization)",
                    "✓ 'holstein' → 'Holstein' (proper capitalization)"
                ]
        
        elif parsed_rule.rule_type == RuleType.CLEANING:
            explanation['what_it_does'] = f"Cleans and removes problematic {parsed_rule.field} values"
            if 'duplicate' in parsed_rule.action.lower():
                explanation['examples'] = [
                    "✓ Keeps first occurrence of LOT001",
                    "✗ Removes second occurrence of LOT001",
                    "✓ Preserves unique records"
                ]
        
        elif parsed_rule.rule_type == RuleType.ESTIMATION:
            explanation['what_it_does'] = f"Estimates missing {parsed_rule.field} values based on available data"
            explanation['examples'] = [
                "✓ Missing weight estimated from similar animals",
                "✓ Missing date estimated from age patterns",
                "✓ Confidence score indicates estimation reliability"
            ]
        
        return explanation

