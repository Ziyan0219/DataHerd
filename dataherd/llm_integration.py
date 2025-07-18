import openai
import json
import os
from typing import Dict, Any

class LLMRuleParser:
    def __init__(self):
        # Initialize OpenAI client using environment variables
        self.client = openai.OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_API_BASE")
        )

    def parse_natural_language_to_rule(self, natural_language_text: str, client_name: str = None) -> Dict[str, Any]:
        """
        Uses LLM to parse natural language cleaning rules into structured JSON format.
        """
        system_prompt = """
        You are an expert data cleaning rule parser for cattle lot data. Your job is to convert natural language cleaning rules into structured JSON format.

        The JSON structure should follow this format:
        {
            "rule_name": "Descriptive name for the rule",
            "conditions": [
                {
                    "field": "field_name",
                    "operator": "less_than|greater_than|equals|not_equals|contains|not_contains",
                    "value": numeric_or_string_value,
                    "action": "flag|delete|modify|ready_to_load"
                }
            ],
            "client_specific_adjustments": {
                "client_name": {
                    "field": "field_name",
                    "operator": "operator",
                    "value": adjusted_value,
                    "action": "action"
                }
            }
        }

        Common cattle data fields include:
        - entry_weight: Weight of cattle when entering the lot
        - exit_weight: Weight of cattle when leaving the lot
        - days_on_feed: Number of days cattle spent in the lot
        - breed: Breed of cattle
        - health_status: Health condition
        - feed_conversion_ratio: Efficiency of feed conversion
        - lot_id: Unique identifier for the lot
        - batch_id: Identifier for the batch

        Common actions:
        - flag: Mark the lot for review but keep it
        - delete: Remove the lot from the dataset
        - modify: Change specific values in the lot
        - ready_to_load: Mark the lot as ready for processing

        Parse the following natural language rule into the JSON structure:
        """

        user_prompt = f"""
        Natural language rule: "{natural_language_text}"
        Client name (if applicable): {client_name or "Not specified"}

        Please convert this into the structured JSON format. If the rule mentions client-specific adjustments or if a client name is provided, include appropriate client_specific_adjustments.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )

            # Extract the JSON from the response
            response_text = response.choices[0].message.content.strip()
            
            # Try to extract JSON from the response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            elif "{" in response_text and "}" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                json_text = response_text[json_start:json_end]
            else:
                json_text = response_text

            # Parse the JSON
            parsed_rule = json.loads(json_text)
            return parsed_rule

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON from LLM response: {e}")
            print(f"Raw response: {response_text}")
            # Return a fallback rule
            return {
                "rule_name": "Fallback Rule",
                "conditions": [],
                "client_specific_adjustments": {},
                "error": f"Failed to parse LLM response: {str(e)}"
            }
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return {
                "rule_name": "Error Rule",
                "conditions": [],
                "client_specific_adjustments": {},
                "error": f"LLM call failed: {str(e)}"
            }

    def explain_rule_application(self, rule: Dict[str, Any], lot_data: Dict[str, Any], action_taken: str) -> str:
        """
        Uses LLM to generate a human-readable explanation of why a rule was applied to a lot.
        """
        system_prompt = """
        You are an expert in explaining data cleaning operations for cattle lot data. 
        Given a cleaning rule, lot data, and the action taken, provide a clear, concise explanation 
        of why the action was taken. The explanation should be understandable by farm managers and data operators.
        """

        user_prompt = f"""
        Rule applied: {json.dumps(rule, indent=2)}
        Lot data: {json.dumps(lot_data, indent=2)}
        Action taken: {action_taken}

        Please explain in simple terms why this action was taken for this lot.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Unable to generate explanation: {str(e)}"

    def suggest_rule_improvements(self, rule: Dict[str, Any], batch_results: List[Dict[str, Any]]) -> str:
        """
        Uses LLM to suggest improvements to a rule based on batch processing results.
        """
        system_prompt = """
        You are an expert in optimizing data cleaning rules for cattle lot data. 
        Given a rule and the results of applying it to a batch, suggest improvements 
        to make the rule more effective or accurate.
        """

        user_prompt = f"""
        Current rule: {json.dumps(rule, indent=2)}
        Batch results summary: {json.dumps(batch_results, indent=2)}

        Based on these results, suggest improvements to the rule. Consider:
        - Are the thresholds appropriate?
        - Are there edge cases not being handled?
        - Could the rule be more specific or more general?
        - Are there additional conditions that should be considered?
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Unable to generate suggestions: {str(e)}"


# Example usage and testing
if __name__ == "__main__":
    parser = LLMRuleParser()

    # Test natural language rule parsing
    test_rules = [
        "Flag any lot where the entry weight is below 500 pounds",
        "Delete lots where cattle have been on feed for more than 200 days",
        "For client Elanco, flag lots with entry weight below 450 pounds, but for other clients use 500 pounds",
        "Mark lots as ready to load if exit weight is at least 1200 pounds and feed conversion ratio is below 6.5"
    ]

    for rule_text in test_rules:
        print(f"\nTesting rule: {rule_text}")
        parsed_rule = parser.parse_natural_language_to_rule(rule_text, "Elanco")
        print(f"Parsed rule: {json.dumps(parsed_rule, indent=2)}")

    # Test explanation generation
    sample_rule = {
        "rule_name": "Weight Check",
        "conditions": [
            {"field": "entry_weight", "operator": "less_than", "value": 500, "action": "flag"}
        ]
    }
    
    sample_lot = {
        "lot_id": "LOT001",
        "entry_weight": 450,
        "breed": "Angus"
    }

    explanation = parser.explain_rule_application(sample_rule, sample_lot, "flag")
    print(f"\nExplanation: {explanation}")

