import json
from typing import List, Dict, Any
from dataherd.rule_engine import RuleEngine
from db.schemas import BatchInfo, LotInfo, OperationLog, CleaningRule
from server.utils import SessionLocal
import uuid

class DataProcessor:
    def __init__(self):
        self.rule_engine = RuleEngine()

    def load_batch_data(self, batch_id: str) -> List[Dict[str, Any]]:
        """
        Loads lot data for a given batch from the database.
        """
        db_session = SessionLocal()
        try:
            lots = db_session.query(LotInfo).filter(LotInfo.batch_id == batch_id).all()
            data = []
            for lot in lots:
                lot_dict = {
                    "lot_id": lot.id,
                    "batch_id": lot.batch_id,
                    "lot_name": lot.lot_name,
                    "status": lot.status,
                    "issue_description": lot.issue_description,
                }
                # Merge original_data (JSON string) into the dictionary
                if lot.original_data:
                    original_data_dict = json.loads(lot.original_data)
                    lot_dict.update(original_data_dict)
                data.append(lot_dict)
            return data
        finally:
            db_session.close()

    def save_cleaned_data(self, batch_id: str, cleaned_batch_data: List[Dict[str, Any]], operator_id: str, rules_applied: List[Dict[str, Any]]):
        """
        Saves the cleaned lot data back to the database and logs the operation.
        """
        db_session = SessionLocal()
        try:
            for lot_data in cleaned_batch_data:
                lot_id = lot_data.get("lot_id")
                lot = db_session.query(LotInfo).filter(LotInfo.id == lot_id).first()
                if lot:
                    lot.cleaned_data = json.dumps(lot_data) # Store cleaned data as JSON string
                    lot.status = lot_data.get("status", "cleaned") # Update status
                    lot.issue_description = lot_data.get("issue_description")
                    db_session.add(lot)

            # Log the operation
            operation_log = OperationLog(
                id=str(uuid.uuid4()),
                batch_id=batch_id,
                operator_id=operator_id,
                operation_type="Apply Cleaning Rules",
                operation_details=json.dumps({"rules": rules_applied}),
                operation_result="Success"
            )
            db_session.add(operation_log)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            raise e
        finally:
            db_session.close()

    def preview_cleaning_operation(self, batch_id: str, natural_language_rules: str, client_name: str = None) -> Dict[str, Any]:
        """
        Previews the data cleaning operation without applying changes to the database.
        Returns the potential changes and a summary.
        """
        db_session = SessionLocal()
        try:
            # Load current rules for the client
            current_rules_db = db_session.query(CleaningRule).filter(CleaningRule.client_name == client_name).all()
            current_rules_parsed = [json.loads(rule.rule_json) for rule in current_rules_db]

            # Parse the new natural language rules
            from dataherd.llm_integration import LLMRuleParser
            llm_parser = LLMRuleParser()
            new_rule_parsed = llm_parser.parse_natural_language_to_rule(natural_language_rules, client_name)
            
            # Combine current rules with the new rule for preview
            rules_for_preview = current_rules_parsed + [new_rule_parsed]

            # Load batch data
            batch_data = self.load_batch_data(batch_id)

            # Apply rules in preview mode
            preview_cleaned_data, actions_summary = self.rule_engine.apply_rules_to_batch(batch_data, rules_for_preview, client_name)

            # Compare original with previewed data to show changes
            original_data_map = {lot["lot_id"]: lot for lot in batch_data}
            changes = []
            for lot_preview in preview_cleaned_data:
                lot_id = lot_preview["lot_id"]
                original_lot = original_data_map.get(lot_id)
                if original_lot and original_lot != lot_preview:
                    changes.append({
                        "lot_id": lot_id,
                        "original": original_lot,
                        "preview": lot_preview,
                        "actions": [action for action in actions_summary if action.get("lot_id") == lot_id]
                    })
            
            # Identify deleted lots
            deleted_lots = []
            preview_lot_ids = {lot["lot_id"] for lot in preview_cleaned_data}
            for lot_id, original_lot in original_data_map.items():
                if lot_id not in preview_lot_ids:
                    deleted_lots.append({
                        "lot_id": lot_id,
                        "original": original_lot,
                        "actions": [action for action in actions_summary if action.get("lot_id") == lot_id]
                    })

            return {
                "preview_data": preview_cleaned_data,
                "changes": changes,
                "deleted_lots": deleted_lots,
                "actions_summary": actions_summary
            }
        finally:
            db_session.close()

    def rollback_operation(self, batch_id: str, operation_log_id: str):
        """
        Rolls back a specific cleaning operation by restoring previous data states.
        This is a simplified rollback. A full rollback system would involve versioning.
        For now, it will restore the `cleaned_data` to `original_data` for the affected lots.
        """
        db_session = SessionLocal()
        try:
            # Find the operation to rollback
            operation_to_rollback = db_session.query(OperationLog).filter(OperationLog.id == operation_log_id).first()
            if not operation_to_rollback:
                raise ValueError("Operation log not found.")

            # Assuming the operation was 'Apply Cleaning Rules' and we need to revert lots to original state
            # In a more complex system, you'd store diffs or snapshots.
            lots_in_batch = db_session.query(LotInfo).filter(LotInfo.batch_id == batch_id).all()
            for lot in lots_in_batch:
                if lot.cleaned_data: # Only revert if it was cleaned
                    lot.cleaned_data = None # Clear cleaned data
                    lot.status = "original" # Reset status
                    lot.issue_description = None
                    db_session.add(lot)
            
            # Log the rollback operation
            rollback_log = OperationLog(
                id=str(uuid.uuid4()),
                batch_id=batch_id,
                operator_id=operation_to_rollback.operator_id, # Assuming same operator
                operation_type="Rollback",
                operation_details=f"Rolled back operation {operation_log_id}",
                operation_result="Success"
            )
            db_session.add(rollback_log)
            db_session.commit()
            return {"status": 200, "message": f"Batch {batch_id} rolled back successfully."}
        except Exception as e:
            db_session.rollback()
            raise e
        finally:
            db_session.close()


# Example Usage (for testing purposes)
if __name__ == "__main__":
    # This part would require a running database and some initial data
    # For a real test, you'd populate the database with BatchInfo and LotInfo
    # and some CleaningRules.
    print("DataProcessor example usage requires a database setup.")
    print("Please ensure your database is initialized and populated with sample data.")

    # Mocking a session and data for demonstration
    class MockLotInfo:
        def __init__(self, id, batch_id, lot_name, original_data, cleaned_data=None, status="original", issue_description=None):
            self.id = id
            self.batch_id = batch_id
            self.lot_name = lot_name
            self.original_data = original_data
            self.cleaned_data = cleaned_data
            self.status = status
            self.issue_description = issue_description

    class MockCleaningRule:
        def __init__(self, id, client_name, rule_name, rule_json, is_permanent=False):
            self.id = id
            self.client_name = client_name
            self.rule_name = rule_name
            self.rule_json = rule_json
            self.is_permanent = is_permanent

    class MockSession:
        def __init__(self):
            self.lots = [
                MockLotInfo("lot1", "batch_A", "Lot 1", json.dumps({"entry_weight": 480, "breed": "Angus"})),
                MockLotInfo("lot2", "batch_A", "Lot 2", json.dumps({"entry_weight": 550, "breed": "Hereford"})),
                MockLotInfo("lot3", "batch_A", "Lot 3", json.dumps({"entry_weight": 1600, "breed": "Simmental"})),
            ]
            self.rules = [
                MockCleaningRule("rule1", "Elanco", "Weight Check", json.dumps({
                    "rule_name": "Weight Check",
                    "conditions": [
                        {"field": "entry_weight", "operator": "less_than", "value": 500, "action": "flag"}
                    ],
                    "client_specific_adjustments": {
                        "Elanco": {"field": "entry_weight", "operator": "less_than", "value": 450, "action": "flag"}
                    }
                }))
            ]
            self.logs = []

        def query(self, model):
            if model == LotInfo:
                return self
            elif model == CleaningRule:
                return self
            elif model == OperationLog:
                return self
            return self

        def filter(self, *args, **kwargs):
            # Simplified filter for demonstration
            if "batch_id" in kwargs:
                self.lots = [lot for lot in self.lots if lot.batch_id == kwargs["batch_id"]]
            if "client_name" in kwargs:
                self.rules = [rule for rule in self.rules if rule.client_name == kwargs["client_name"]]
            if "id" in kwargs:
                if self.lots and self.lots[0].id == kwargs["id"]:
                    self.lots = [self.lots[0]]
                elif self.rules and self.rules[0].id == kwargs["id"]:
                    self.rules = [self.rules[0]]
                elif self.logs and self.logs[0].id == kwargs["id"]:
                    self.logs = [self.logs[0]]
                else:
                    return self # Return self to allow .first() or .all()
            return self

        def all(self):
            if hasattr(self, "lots") and self.lots:
                return self.lots
            if hasattr(self, "rules") and self.rules:
                return self.rules
            if hasattr(self, "logs") and self.logs:
                return self.logs
            return []

        def first(self):
            if hasattr(self, "lots") and self.lots:
                return self.lots[0]
            if hasattr(self, "rules") and self.rules:
                return self.rules[0]
            if hasattr(self, "logs") and self.logs:
                return self.logs[0]
            return None

        def add(self, obj):
            if isinstance(obj, LotInfo):
                # In a real scenario, you'd update existing or add new
                pass
            elif isinstance(obj, OperationLog):
                self.logs.append(obj)

        def commit(self):
            pass

        def rollback(self):
            pass

        def close(self):
            pass

    # Mock SessionLocal to return our mock session
    def mock_session_local():
        return MockSession()

    # Temporarily replace SessionLocal for testing
    import sys
    sys.modules["server.utils"].SessionLocal = mock_session_local

    processor = DataProcessor()

    # Test Preview
    print("\n--- Testing Preview --- ")
    preview_result = processor.preview_cleaning_operation("batch_A", "flag lot if entry weight below 490", "Elanco")
    print("Preview Data:", json.dumps(preview_result["preview_data"], indent=2))
    print("Changes:", json.dumps(preview_result["changes"], indent=2))
    print("Deleted Lots:", json.dumps(preview_result["deleted_lots"], indent=2))
    print("Actions Summary:", json.dumps(preview_result["actions_summary"], indent=2))

    # Test Rollback (conceptual, as no actual DB changes are made in mock)
    print("\n--- Testing Rollback (Conceptual) --- ")
    try:
        # Simulate an operation log entry for rollback
        mock_op_log_id = str(uuid.uuid4())
        mock_op_log = OperationLog(
            id=mock_op_log_id,
            batch_id="batch_A",
            operator_id="test_user",
            operation_type="Apply Cleaning Rules",
            operation_details="{}",
            operation_result="Success"
        )
        mock_session_local().logs.append(mock_op_log)

        rollback_status = processor.rollback_operation("batch_A", mock_op_log_id)
        print(rollback_status)
    except Exception as e:
        print(f"Rollback failed: {e}")

    # Restore original SessionLocal
    # This part is crucial in a real application to avoid side effects
    # For this isolated test, it's less critical but good practice.
    # sys.modules["server.utils"].SessionLocal = original_session_local 


