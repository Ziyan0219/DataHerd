import json
from typing import List, Dict, Any
from datetime import datetime
from db.schemas import OperationLog, BatchInfo, CleaningRule
from server.utils import SessionLocal

class ReportGenerator:
    def __init__(self):
        pass

    def generate_operation_report(self, batch_id: str = None, operator_id: str = None, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """
        Generates a detailed report of data cleaning operations.
        Filters can be applied by batch_id, operator_id, and date range.
        """
        db_session = SessionLocal()
        try:
            query = db_session.query(OperationLog)

            if batch_id:
                query = query.filter(OperationLog.batch_id == batch_id)
            if operator_id:
                query = query.filter(OperationLog.operator_id == operator_id)
            if start_date:
                start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                query = query.filter(OperationLog.timestamp >= start_dt)
            if end_date:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                query = query.filter(OperationLog.timestamp <= end_dt)

            operations = query.order_by(OperationLog.timestamp.desc()).all()

            report_data = {
                "report_title": "Data Cleaning Operations Report",
                "generated_at": datetime.now().isoformat(),
                "filters_applied": {
                    "batch_id": batch_id,
                    "operator_id": operator_id,
                    "start_date": start_date,
                    "end_date": end_date
                },
                "operations": []
            }

            for op in operations:
                rule_info = None
                if op.rule_id:
                    rule = db_session.query(CleaningRule).filter(CleaningRule.id == op.rule_id).first()
                    if rule:
                        rule_info = {
                            "rule_name": rule.rule_name,
                            "rule_description": rule.rule_description,
                            "is_permanent": rule.is_permanent
                        }

                batch_info = None
                if op.batch_id:
                    batch = db_session.query(BatchInfo).filter(BatchInfo.id == op.batch_id).first()
                    if batch:
                        batch_info = {
                            "batch_name": batch.batch_name,
                            "client_name": batch.client_name
                        }

                report_data["operations"].append({
                    "operation_id": op.id,
                    "timestamp": op.timestamp.isoformat(),
                    "operator_id": op.operator_id,
                    "operation_type": op.operation_type,
                    "batch_id": op.batch_id,
                    "batch_info": batch_info,
                    "rule_info": rule_info,
                    "operation_details": json.loads(op.operation_details) if op.operation_details else {},
                    "operation_result": op.operation_result
                })

            return report_data
        finally:
            db_session.close()


# Example Usage (for testing purposes)
if __name__ == "__main__":
    print("ReportGenerator example usage requires a database setup and populated data.")
    print("Please ensure your database is initialized and populated with sample data.")

    # Mocking a session and data for demonstration
    class MockOperationLog:
        def __init__(self, id, batch_id, operator_id, operation_type, timestamp, rule_id=None, operation_details=None, operation_result=None):
            self.id = id
            self.batch_id = batch_id
            self.operator_id = operator_id
            self.operation_type = operation_type
            self.timestamp = timestamp
            self.rule_id = rule_id
            self.operation_details = operation_details
            self.operation_result = operation_result

    class MockBatchInfo:
        def __init__(self, id, batch_name, client_name):
            self.id = id
            self.batch_name = batch_name
            self.client_name = client_name

    class MockCleaningRule:
        def __init__(self, id, rule_name, rule_description, is_permanent):
            self.id = id
            self.rule_name = rule_name
            self.rule_description = rule_description
            self.is_permanent = is_permanent

    class MockSession:
        def __init__(self):
            self.operation_logs = [
                MockOperationLog("op1", "batch_A", "user1", "Apply Cleaning Rules", datetime(2025, 7, 17, 10, 0, 0), "rule1", json.dumps({"rules": ["weight check"]}), "Success"),
                MockOperationLog("op2", "batch_B", "user2", "Preview Cleaning", datetime(2025, 7, 17, 11, 0, 0), None, json.dumps({"rules": ["breed check"]}), "Previewed"),
                MockOperationLog("op3", "batch_A", "user1", "Rollback", datetime(2025, 7, 18, 9, 0, 0), None, json.dumps({"rolled_back_op_id": "op1"}), "Success"),
            ]
            self.batches = [
                MockBatchInfo("batch_A", "Batch Alpha", "Elanco"),
                MockBatchInfo("batch_B", "Batch Beta", "ClientX"),
            ]
            self.rules = [
                MockCleaningRule("rule1", "Weight Check", "Flags lots with abnormal weight", True)
            ]

        def query(self, model):
            if model == OperationLog:
                return self
            elif model == BatchInfo:
                return self
            elif model == CleaningRule:
                return self
            return self

        def filter(self, *args, **kwargs):
            # Simplified filter for demonstration
            filtered_list = []
            if self.model == OperationLog:
                for op in self.operation_logs:
                    match = True
                    if "batch_id" in kwargs and op.batch_id != kwargs["batch_id"]:
                        match = False
                    if "operator_id" in kwargs and op.operator_id != kwargs["operator_id"]:
                        match = False
                    if "timestamp" in kwargs:
                        if isinstance(kwargs["timestamp"], tuple):
                            if kwargs["timestamp"][0] == ">=" and op.timestamp < kwargs["timestamp"][1]:
                                match = False
                            if kwargs["timestamp"][0] == "<=" and op.timestamp > kwargs["timestamp"][1]:
                                match = False
                    if match:
                        filtered_list.append(op)
                self.operation_logs = filtered_list
            elif self.model == BatchInfo:
                for batch in self.batches:
                    match = True
                    if "id" in kwargs and batch.id != kwargs["id"]:
                        match = False
                    if match:
                        filtered_list.append(batch)
                self.batches = filtered_list
            elif self.model == CleaningRule:
                for rule in self.rules:
                    match = True
                    if "id" in kwargs and rule.id != kwargs["id"]:
                        match = False
                    if match:
                        filtered_list.append(rule)
                self.rules = filtered_list
            return self

        def order_by(self, *args):
            # Simplified order_by
            if self.model == OperationLog:
                self.operation_logs.sort(key=lambda x: x.timestamp, reverse=True)
            return self

        def all(self):
            if self.model == OperationLog:
                return self.operation_logs
            elif self.model == BatchInfo:
                return self.batches
            elif self.model == CleaningRule:
                return self.rules
            return []

        def first(self):
            if self.model == BatchInfo and self.batches:
                return self.batches[0]
            elif self.model == CleaningRule and self.rules:
                return self.rules[0]
            return None

        def __call__(self, model):
            self.model = model
            return self

    # Temporarily replace SessionLocal for testing
    import sys
    sys.modules["server.utils"].SessionLocal = lambda: MockSession()

    generator = ReportGenerator()

    # Test generating a report for a specific batch
    print("\n--- Report for Batch A ---")
    report_batch_a = generator.generate_operation_report(batch_id="batch_A")
    print(json.dumps(report_batch_a, indent=2))

    # Test generating a report for a specific operator
    print("\n--- Report for User 2 ---")
    report_user_2 = generator.generate_operation_report(operator_id="user2")
    print(json.dumps(report_user_2, indent=2))

    # Test generating a report for a date range
    print("\n--- Report for July 17, 2025 ---")
    report_date_range = generator.generate_operation_report(start_date="2025-07-17", end_date="2025-07-17")
    print(json.dumps(report_date_range, indent=2))

    # Restore original SessionLocal (conceptual)
    # sys.modules["server.utils"].SessionLocal = original_session_local


