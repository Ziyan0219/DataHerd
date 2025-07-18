from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class CleaningRule(Base):
    __tablename__ = 'cleaning_rules'
    id = Column(String, primary_key=True, index=True)
    client_name = Column(String, index=True, nullable=False) # Elanco client name
    rule_name = Column(String, nullable=False) # e.g., 'Weight Anomaly Check'
    rule_description = Column(Text, nullable=True) # Natural language description of the rule
    rule_json = Column(Text, nullable=False) # JSON representation of the rule logic
    is_permanent = Column(Boolean, default=False) # Whether this rule is permanently applied
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<CleaningRule(id='{self.id}', client_name='{self.client_name}', rule_name='{self.rule_name}')>"

class OperationLog(Base):
    __tablename__ = 'operation_logs'
    id = Column(String, primary_key=True, index=True)
    batch_id = Column(String, nullable=False) # ID of the batch being cleaned
    lot_id = Column(String, nullable=True) # ID of the specific lot if applicable
    operator_id = Column(String, nullable=False) # User who performed the operation
    operation_type = Column(String, nullable=False) # e.g., 'Apply Rule', 'Rollback', 'Preview'
    rule_id = Column(String, ForeignKey('cleaning_rules.id'), nullable=True) # Rule applied, if any
    operation_details = Column(Text, nullable=True) # Details of the operation (e.g., rule parameters, data changes)
    operation_result = Column(Text, nullable=True) # Result of the operation (e.g., 'Success', 'Failed', 'Previewed')
    timestamp = Column(DateTime, default=func.now())

    rule = relationship("CleaningRule")

    def __repr__(self):
        return f"<OperationLog(id='{self.id}', batch_id='{self.batch_id}', operation_type='{self.operation_type}')>"

class BatchInfo(Base):
    __tablename__ = 'batch_info'
    id = Column(String, primary_key=True, index=True)
    batch_name = Column(String, nullable=False)
    client_name = Column(String, index=True, nullable=False)
    data_source_path = Column(String, nullable=True) # Path to the raw data file/source
    status = Column(String, default='pending') # e.g., 'pending', 'cleaned', 'in_progress'
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<BatchInfo(id='{self.id}', batch_name='{self.batch_name}', client_name='{self.client_name}')>"

class LotInfo(Base):
    __tablename__ = 'lot_info'
    id = Column(String, primary_key=True, index=True)
    batch_id = Column(String, ForeignKey('batch_info.id'), nullable=False)
    lot_name = Column(String, nullable=False)
    original_data = Column(Text, nullable=True) # Store original lot data (e.g., JSON string)
    cleaned_data = Column(Text, nullable=True) # Store cleaned lot data (e.g., JSON string)
    status = Column(String, default='original') # e.g., 'original', 'flagged', 'cleaned', 'deleted'
    issue_description = Column(Text, nullable=True) # Description of issues found
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    batch = relationship("BatchInfo")

    def __repr__(self):
        return f"<LotInfo(id='{self.id}', lot_name='{self.lot_name}', batch_id='{self.batch_id}')>"

