import json
import re
from typing import Dict, Any, List

class RuleEngine:
    def __init__(self):
        # This will store the parsed and executable rules
        self.rules = {}

    def parse_natural_language_rule(self, natural_language_text: str) -> Dict[str, Any]:
        """
        Parses natural language text to extract structured cleaning rules.
        This is a placeholder. In a real application, this would involve:
        1. Sending the natural_language_text to an LLM (e.g., OpenAI, Gemini).
        2. The LLM would be prompted to output a structured JSON representing the rule.
           Example JSON structure:
           {
               "rule_name": "Weight Anomaly Check",
               "conditions": [
                   {"field": "entry_weight", "operator": "less_than", "value": 500, "action": "flag"},
                   {"field": "entry_weight", "operator": "greater_than", "value": 1500, "action": "delete"}
               ],
               "client_specific_adjustments": {
                   "client_A": {"field": "entry_weight", "operator": "less_than", "value": 450},
                   "client_B": {"field": "entry_weight", "operator": "greater_than", "value": 1600}
               }
           }
        """
        # Placeholder for LLM interaction
        # For demonstration, let's simulate a simple rule parsing
        if "weight below 500" in natural_language_text.lower():
            return {
                "rule_name": "Simulated Weight Check",
                "conditions": [
                    {"field": "entry_weight", "operator": "less_than", "value": 500, "action": "flag"}
                ],
                "client_specific_adjustments": {}
            }
        elif "delete lot if weight above 1500" in natural_language_text.lower():
            return {
                "rule_name": "Simulated Delete Weight Check",
                "conditions": [
                    {"field": "entry_weight", "operator": "greater_than", "value": 1500, "action": "delete"}
                ],
                "client_specific_adjustments": {}
            }
        else:
            return {"rule_name": "Default Rule", "conditions": [], "client_specific_adjustments": {}}

    def apply_rule_to_lot(self, lot_data: Dict[str, Any], rule: Dict[str, Any], client_name: str = None) -> Dict[str, Any]:
        """
        Applies a single structured rule to a lot of data.
        Returns the modified lot data and the action taken.
        """
        modified_lot_data = lot_data.copy()
        action_taken = "none"

        conditions = rule.get("conditions", [])
        client_adjustments = rule.get("client_specific_adjustments", {})

        # Apply client-specific adjustments if available
        if client_name and client_name in client_adjustments:
            adjusted_rule = rule.copy()
            adjusted_rule["conditions"].append(client_adjustments[client_name])
            conditions = adjusted_rule["conditions"]

        for condition in conditions:
            field = condition.get("field")
            operator = condition.get("operator")
            value = condition.get("value")
            action = condition.get("action")

            if field in modified_lot_data:
                field_value = modified_lot_data[field]
                if operator == "less_than" and field_value < value:
                    action_taken = action
                    break
                elif operator == "greater_than" and field_value > value:
                    action_taken = action
                    break
                # Add more operators as needed (e.g., equals, not_equals, contains)

        return modified_lot_data, action_taken

    def apply_rules_to_batch(self, batch_data: List[Dict[str, Any]], rules: List[Dict[str, Any]], client_name: str = None) -> List[Dict[str, Any]]:
        """
        Applies a list of structured rules to an entire batch of data.
        Returns the cleaned batch data and a summary of actions taken.
        """
        cleaned_batch_data = []
        actions_summary = []

        for lot_data in batch_data:
            original_lot_data = lot_data.copy()
            current_lot_data = lot_data.copy()
            lot_actions = []

            for rule in rules:
                modified_lot, action_taken = self.apply_rule_to_lot(current_lot_data, rule, client_name)
                if action_taken != "none":
                    lot_actions.append({"rule_name": rule["rule_name"], "action": action_taken, "lot_id": current_lot_data.get("lot_id")})
                    if action_taken == "delete":
                        current_lot_data = None # Mark for deletion
                        break # No more rules apply if deleted
                    elif action_taken == "flag":
                        current_lot_data["status"] = "flagged" # Example of flagging
                        current_lot_data["issue_description"] = rule["rule_name"]

            if current_lot_data is not None:
                cleaned_batch_data.append(current_lot_data)
            
            if lot_actions:
                actions_summary.extend(lot_actions)

        return cleaned_batch_data, actions_summary


# Example Usage (for testing purposes)
if __name__ == "__main__":
    engine = RuleEngine()

    # Simulate natural language input from user
    nl_rule_1 = "flag lot if entry weight below 500"
    nl_rule_2 = "delete lot if weight above 1500"

    # Parse rules (LLM interaction would happen here)
    rule_1 = engine.parse_natural_language_rule(nl_rule_1)
    rule_2 = engine.parse_natural_language_rule(nl_rule_2)

    print(f"Parsed Rule 1: {rule_1}")
    print(f"Parsed Rule 2: {rule_2}")

    # Simulate batch data
    sample_batch = [
        {"lot_id": "lot_001", "entry_weight": 450, "status": "original"},
        {"lot_id": "lot_002", "entry_weight": 600, "status": "original"},
        {"lot_id": "lot_003", "entry_weight": 1600, "status": "original"},
        {"lot_id": "lot_004", "entry_weight": 1400, "status": "original"},
    ]

    # Apply rules to the batch
    cleaned_data, summary = engine.apply_rules_to_batch(sample_batch, [rule_1, rule_2])

    print("\nCleaned Data:")
    for lot in cleaned_data:
        print(lot)

    print("\nActions Summary:")
    for action in summary:
        print(action)

    # Example with client-specific adjustment
    nl_rule_3 = "flag lot if entry weight below 500, but for client_A, flag if below 450"
    rule_3 = {
        "rule_name": "Weight Check with Client Adjustment",
        "conditions": [
            {"field": "entry_weight", "operator": "less_than", "value": 500, "action": "flag"}
        ],
        "client_specific_adjustments": {
            "client_A": {"field": "entry_weight", "operator": "less_than", "value": 450, "action": "flag"}
        }
    }

    sample_batch_2 = [
        {"lot_id": "lot_005", "entry_weight": 470, "status": "original"},
        {"lot_id": "lot_006", "entry_weight": 430, "status": "original"},
    ]

    print("\nApplying rule with client_A adjustment:")
    cleaned_data_client_a, summary_client_a = engine.apply_rules_to_batch(sample_batch_2, [rule_3], client_name="client_A")
    for lot in cleaned_data_client_a:
        print(lot)
    print("Actions Summary for client_A:")
    for action in summary_client_a:
        print(action)

    print("\nApplying rule without client_A adjustment (default):")
    cleaned_data_default, summary_default = engine.apply_rules_to_batch(sample_batch_2, [rule_3])
    for lot in cleaned_data_default:
        print(lot)
    print("Actions Summary for default:")
    for action in summary_default:
        print(action)


