"""
DataHerd Database Models

This module contains the database models specifically designed for cattle data cleaning operations.
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Integer, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class CattleRecord(Base):
    """Model for storing cattle data records."""
    __tablename__ = 'cattle_records'
    
    id = Column(Integer, primary_key=True, index=True)
    lot_id = Column(String, nullable=False, index=True)
    weight = Column(Float, nullable=True)
    breed = Column(String, nullable=True)
    birth_date = Column(DateTime, nullable=True)
    health_status = Column(String, nullable=True)
    feed_type = Column(String, nullable=True)
    batch_id = Column(String, nullable=True, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<CattleRecord(lot_id='{self.lot_id}', weight={self.weight}, breed='{self.breed}')>"

class CleaningRule(Base):
    """Model for storing data cleaning rules."""
    __tablename__ = 'cleaning_rules'
    
    rule_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g., 'Weight Anomaly Check'
    description = Column(Text, nullable=True)  # Natural language description of the rule
    rule_type = Column(String, nullable=False)  # validation, standardization, cleaning, estimation
    field = Column(String, nullable=True)  # Field to apply rule to
    condition = Column(Text, nullable=True)  # Python condition string
    action = Column(String, nullable=True)  # Action to take
    parameters = Column(Text, nullable=True)  # JSON parameters
    confidence = Column(Float, default=0.0)  # Rule confidence score
    client_context = Column(String, index=True, nullable=True)  # Client context
    is_permanent = Column(Boolean, default=False)  # Whether this rule is permanently applied
    is_active = Column(Boolean, default=True)  # Whether rule is active
    usage_count = Column(Integer, default=0)  # Number of times used
    success_rate = Column(Float, default=0.0)  # Success rate percentage
    last_used = Column(DateTime, nullable=True)  # Last usage timestamp
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<CleaningRule(rule_id='{self.rule_id}', name='{self.name}', client_context='{self.client_context}')>"

class OperationLog(Base):
    """Model for storing operation logs."""
    __tablename__ = 'operation_logs'
    
    operation_id = Column(String, primary_key=True, index=True)
    batch_id = Column(String, nullable=False)  # ID of the batch being cleaned
    rule_type = Column(String, nullable=True)  # Type of rule applied
    rule_description = Column(Text, nullable=True)  # Description of the rule
    changes_made = Column(Text, nullable=True)  # JSON string of changes made
    client_name = Column(String, nullable=True)  # Client name
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<OperationLog(operation_id='{self.operation_id}', batch_id='{self.batch_id}', rule_type='{self.rule_type}')>"

class BatchInfo(Base):
    """Model for storing batch information."""
    __tablename__ = 'batch_info'
    
    batch_id = Column(String, primary_key=True, index=True)
    file_path = Column(String, nullable=True)  # Path to the raw data file/source
    record_count = Column(Integer, default=0)  # Number of records in batch
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return f"<BatchInfo(batch_id='{self.batch_id}', record_count={self.record_count})>"

class LotInfo(Base):
    """Model for storing lot information."""
    __tablename__ = 'lot_info'
    
    id = Column(String, primary_key=True, index=True)
    batch_id = Column(String, ForeignKey('batch_info.id'), nullable=False)
    lot_name = Column(String, nullable=False)
    original_data = Column(Text, nullable=True)  # Store original lot data (e.g., JSON string)
    cleaned_data = Column(Text, nullable=True)  # Store cleaned lot data (e.g., JSON string)
    status = Column(String, default='original')  # e.g., 'original', 'flagged', 'cleaned', 'deleted'
    issue_description = Column(Text, nullable=True)  # Description of issues found
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    batch = relationship("BatchInfo")

    def __repr__(self):
        return f"<LotInfo(id='{self.id}', lot_name='{self.lot_name}', batch_id='{self.batch_id}')>"


class RuleApplication(Base):
    """Model for tracking rule applications."""
    __tablename__ = 'rule_applications'
    
    application_id = Column(String, primary_key=True, index=True)
    rule_id = Column(String, ForeignKey('cleaning_rules.rule_id'), nullable=False)
    batch_id = Column(String, nullable=False)
    applied_at = Column(DateTime, default=func.now())
    success = Column(Boolean, default=True)
    changes_made = Column(Integer, default=0)

    def __repr__(self):
        return f"<RuleApplication(application_id='{self.application_id}', rule_id='{self.rule_id}', batch_id='{self.batch_id}')>"


class ClientTemplate(Base):
    """Model for storing client-specific rule templates."""
    __tablename__ = 'client_templates'
    
    template_id = Column(String, primary_key=True, index=True)
    client_name = Column(String, nullable=False, index=True)
    template_name = Column(String, nullable=False)
    template_rules = Column(Text, nullable=False)  # JSON string of rule IDs
    created_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<ClientTemplate(template_id='{self.template_id}', client_name='{self.client_name}', template_name='{self.template_name}')>"

