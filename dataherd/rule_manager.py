import json
import uuid
from typing import Dict, Any, List
from db.schemas import CleaningRule, BatchInfo
from server.utils import SessionLocal
from dataherd.llm_integration import LLMRuleParser

class RuleManager:
    def __init__(self):
        self.llm_parser = LLMRuleParser()

    def get_rules_for_client(self, client_name: str) -> List[Dict[str, Any]]:
        """
        Retrieves all cleaning rules for a given client.
        """
        db_session = SessionLocal()
        try:
            rules = db_session.query(CleaningRule).filter(CleaningRule.client_name == client_name).all()
            return [json.loads(rule.rule_json) for rule in rules]
        finally:
            db_session.close()

    def save_rule(self, client_name: str, natural_language_rule: str, is_permanent: bool = False) -> Dict[str, Any]:
        """
        Parses a natural language rule and saves it to the database.
        If a similar rule already exists and is not permanent, it might be updated.
        """
        db_session = SessionLocal()
        try:
            parsed_rule = self.llm_parser.parse_natural_language_to_rule(natural_language_rule, client_name)
            rule_id = str(uuid.uuid4())

            # Check if a similar rule exists for the client (simplified check)
            existing_rule = db_session.query(CleaningRule).filter(
                CleaningRule.client_name == client_name,
                CleaningRule.rule_name == parsed_rule.get("rule_name")
            ).first()

            if existing_rule and not existing_rule.is_permanent:
                # Update existing non-permanent rule
                existing_rule.rule_json = json.dumps(parsed_rule)
                existing_rule.is_permanent = is_permanent
                db_session.add(existing_rule)
                db_session.commit()
                return {"status": 200, "message": "Rule updated successfully", "rule_id": existing_rule.id}
            elif existing_rule and existing_rule.is_permanent and is_permanent:
                # If both are permanent, do not overwrite, but log it
                return {"status": 400, "message": "Permanent rule with this name already exists.", "rule_id": existing_rule.id}
            else:
                # Create new rule
                new_rule = CleaningRule(
                    id=rule_id,
                    client_name=client_name,
                    rule_name=parsed_rule.get("rule_name", "Unnamed Rule"),
                    rule_description=natural_language_rule,
                    rule_json=json.dumps(parsed_rule),
                    is_permanent=is_permanent
                )
                db_session.add(new_rule)
                db_session.commit()
                return {"status": 200, "message": "Rule saved successfully", "rule_id": rule_id}
        except Exception as e:
            db_session.rollback()
            raise e
        finally:
            db_session.close()

    def update_permanent_rule(self, rule_id: str, new_natural_language_rule: str) -> Dict[str, Any]:
        """
        Updates an existing permanent rule based on new natural language input.
        """
        db_session = SessionLocal()
        try:
            rule_to_update = db_session.query(CleaningRule).filter(CleaningRule.id == rule_id).first()
            if not rule_to_update:
                raise ValueError("Rule not found.")
            if not rule_to_update.is_permanent:
                raise ValueError("Only permanent rules can be updated via this method.")

            client_name = rule_to_update.client_name
            updated_parsed_rule = self.llm_parser.parse_natural_language_to_rule(new_natural_language_rule, client_name)

            rule_to_update.rule_json = json.dumps(updated_parsed_rule)
            rule_to_update.rule_description = new_natural_language_rule
            db_session.add(rule_to_update)
            db_session.commit()
            return {"status": 200, "message": "Permanent rule updated successfully", "rule_id": rule_id}
        except Exception as e:
            db_session.rollback()
            raise e
        finally:
            db_session.close()

    def get_batch_cleaning_rules(self, batch_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves cleaning rules associated with a specific batch.
        This could be based on client name or specific rules stored for the batch.
        For now, it fetches rules based on the batch's client name.
        """
        db_session = SessionLocal()
        try:
            batch_info = db_session.query(BatchInfo).filter(BatchInfo.id == batch_id).first()
            if not batch_info:
                return []
            return self.get_rules_for_client(batch_info.client_name)
        finally:
            db_session.close()


# Example Usage (for testing purposes)
if __name__ == "__main__":
    print("RuleManager example usage requires a database setup.")
    print("Please ensure your database is initialized and populated with sample data.")

    # Mocking a session and data for demonstration
    class MockCleaningRule:
        def __init__(self, id, client_name, rule_name, rule_json, is_permanent=False):
            self.id = id
            self.client_name = client_name
            self.rule_name = rule_name
            self.rule_json = rule_json
            self.is_permanent = is_permanent

    class MockBatchInfo:
        def __init__(self, id, client_name):
            self.id = id
            self.client_name = client_name

    class MockSession:
        def __init__(self):
            self.rules = [
                MockCleaningRule("rule_perm_1", "Elanco", "Min Weight", json.dumps({"rule_name": "Min Weight", "conditions": [{"field": "entry_weight", "operator": "greater_than", "value": 100, "action": "flag"}]}), True),
                MockCleaningRule("rule_temp_1", "Elanco", "Max Weight", json.dumps({"rule_name": "Max Weight", "conditions": [{"field": "entry_weight", "operator": "less_than", "value": 2000, "action": "flag"}]}), False),
            ]
            self.batches = [
                MockBatchInfo("batch_A", "Elanco")
            ]

        def query(self, model):
            if model == CleaningRule:
                return self
            elif model == BatchInfo:
                return self
            return self

        def filter(self, *args, **kwargs):
            if "client_name" in kwargs:
                self.rules = [r for r in self.rules if r.client_name == kwargs["client_name"]]
            if "rule_name" in kwargs:
                self.rules = [r for r in self.rules if r.rule_name == kwargs["rule_name"]]
            if "id" in kwargs:
                self.rules = [r for r in self.rules if r.id == kwargs["id"]]
                self.batches = [b for b in self.batches if b.id == kwargs["id"]]
            return self

        def all(self):
            if hasattr(self, "rules") and self.rules:
                return self.rules
            return []

        def first(self):
            if hasattr(self, "rules") and self.rules:
                return self.rules[0]
            if hasattr(self, "batches") and self.batches:
                return self.batches[0]
            return None

        def add(self, obj):
            if isinstance(obj, CleaningRule):
                self.rules.append(obj)

        def commit(self):
            pass

        def rollback(self):
            pass

        def close(self):
            pass

    # Mock SessionLocal to return our mock session
    import sys
    sys.modules["server.utils"].SessionLocal = lambda: MockSession()

    manager = RuleManager()

    # Test saving a new rule
    print("\n--- Test Saving New Rule ---")
    result = manager.save_rule("Elanco", "flag lot if entry weight is less than 400", is_permanent=False)
    print(result)

    # Test saving a permanent rule
    result_perm = manager.save_rule("Elanco", "permanently delete lot if exit weight is above 1800", is_permanent=True)
    print(result_perm)

    # Test updating a permanent rule
    if result_perm["status"] == 200:
        try:
            update_result = manager.update_permanent_rule(result_perm["rule_id"], "permanently delete lot if exit weight is above 1900")
            print(update_result)
        except Exception as e:
            print(f"Update permanent rule failed: {e}")

    # Test getting rules for a client
    print("\n--- Test Get Rules for Client ---")
    elanco_rules = manager.get_rules_for_client("Elanco")
    for rule in elanco_rules:
        print(rule)

    # Test getting batch cleaning rules
    print("\n--- Test Get Batch Cleaning Rules ---")
    batch_rules = manager.get_batch_cleaning_rules("batch_A")
    for rule in batch_rules:
        print(rule)


