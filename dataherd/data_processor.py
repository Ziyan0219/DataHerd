#!/usr/bin/env python3
"""
DataHerd Data Processor

This module handles data loading, cleaning, preview, and rollback operations
for cattle data management.
"""

import pandas as pd
import numpy as np
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import tempfile
import os

from .nlp_processor import NLPProcessor, ParsedRule
from .rule_manager import RuleManager
from db.models import CattleRecord, BatchInfo, OperationLog
from db.base import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataProcessor:
    """Data processor for cattle data cleaning operations"""
    
    def __init__(self):
        """Initialize the data processor"""
        self.nlp_processor = NLPProcessor()
        self.rule_manager = RuleManager()
        self.data_cache = {}  # Cache for loaded data
        self.backup_cache = {}  # Cache for data backups
    
    def load_data(self, file_path: str, batch_id: str) -> Dict[str, Any]:
        """
        Load data from file and store in database
        
        Args:
            file_path: Path to the data file (CSV, Excel)
            batch_id: Unique identifier for the batch
            
        Returns:
            Dictionary with loading results
        """
        try:
            # Load data based on file type
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_path}")
            
            # Validate data structure
            required_columns = ['lot_id', 'weight', 'breed', 'birth_date', 'health_status']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")
            
            # Store data in cache
            self.data_cache[batch_id] = df.copy()
            
            # Save batch info to database
            self._save_batch_info(batch_id, file_path, len(df))
            
            return {
                'status': 'success',
                'batch_id': batch_id,
                'record_count': len(df),
                'columns': list(df.columns),
                'message': f"Data loaded successfully: {len(df)} records"
            }
            
        except Exception as e:
            logger.error(f"Data loading failed: {e}")
            return {
                'status': 'error',
                'batch_id': batch_id,
                'message': f"Data loading failed: {str(e)}"
            }
    
    def preview_cleaning_operation(self, batch_id: str, rule_text: str, 
                                 client_name: str = "") -> Dict[str, Any]:
        """
        Preview data cleaning operation without applying changes
        
        Args:
            batch_id: Batch identifier
            rule_text: Natural language rule description
            client_name: Client name for context
            
        Returns:
            Dictionary with preview results
        """
        try:
            # Get data from cache
            if batch_id not in self.data_cache:
                return {
                    'status': 'error',
                    'message': f"Batch {batch_id} not found in cache"
                }
            
            df = self.data_cache[batch_id].copy()
            
            # Parse the rule
            parsed_rule = self.nlp_processor.parse_natural_language_rule(rule_text, client_name)
            
            # Apply rule to generate preview
            preview_results = self._apply_rule_preview(df, parsed_rule)
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(df, preview_results)
            
            return {
                'status': 'success',
                'batch_id': batch_id,
                'rule': parsed_rule.description,
                'preview_results': preview_results,
                'quality_metrics': quality_metrics,
                'confidence': parsed_rule.confidence,
                'message': f"Preview generated: {len(preview_results['changes'])} changes identified"
            }
            
        except Exception as e:
            logger.error(f"Preview generation failed: {e}")
            return {
                'status': 'error',
                'message': f"Preview generation failed: {str(e)}"
            }
    
    def apply_cleaning_rules(self, batch_id: str, rule_text: str, 
                           client_name: str = "", save_rule: bool = False) -> Dict[str, Any]:
        """
        Apply cleaning rules to data
        
        Args:
            batch_id: Batch identifier
            rule_text: Natural language rule description
            client_name: Client name for context
            save_rule: Whether to save the rule permanently
            
        Returns:
            Dictionary with operation results
        """
        try:
            # Create backup before applying changes
            self._create_backup(batch_id)
            
            # Get data from cache
            if batch_id not in self.data_cache:
                return {
                    'status': 'error',
                    'message': f"Batch {batch_id} not found in cache"
                }
            
            df = self.data_cache[batch_id]
            
            # Parse the rule
            parsed_rule = self.nlp_processor.parse_natural_language_rule(rule_text, client_name)
            
            # Apply the rule
            changes = self._apply_rule_to_data(df, parsed_rule)
            
            # Save rule if requested
            if save_rule:
                rule_id = self.rule_manager.save_rule(parsed_rule, rule_text, client_name)
            else:
                rule_id = None
            
            # Log the operation
            operation_id = self._log_operation(batch_id, parsed_rule, changes, client_name)
            
            return {
                'status': 'success',
                'batch_id': batch_id,
                'operation_id': operation_id,
                'rule_id': rule_id,
                'changes_applied': len(changes),
                'message': f"Cleaning operation completed: {len(changes)} changes applied"
            }
            
        except Exception as e:
            logger.error(f"Cleaning operation failed: {e}")
            return {
                'status': 'error',
                'message': f"Cleaning operation failed: {str(e)}"
            }
    
    def rollback_operation(self, batch_id: str, operation_id: str) -> Dict[str, Any]:
        """
        Rollback a previous cleaning operation
        
        Args:
            batch_id: Batch identifier
            operation_id: Operation identifier to rollback
            
        Returns:
            Dictionary with rollback results
        """
        try:
            # Check if backup exists
            if batch_id not in self.backup_cache:
                return {
                    'status': 'error',
                    'message': f"No backup found for batch {batch_id}"
                }
            
            # Restore data from backup
            self.data_cache[batch_id] = self.backup_cache[batch_id].copy()
            
            # Log the rollback
            self._log_rollback(batch_id, operation_id)
            
            return {
                'status': 'success',
                'batch_id': batch_id,
                'operation_id': operation_id,
                'message': "Operation rolled back successfully"
            }
            
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return {
                'status': 'error',
                'message': f"Rollback failed: {str(e)}"
            }
    
    def _apply_rule_preview(self, df: pd.DataFrame, parsed_rule: ParsedRule) -> Dict[str, Any]:
        """Apply rule to generate preview without modifying data"""
        changes = []
        
        if parsed_rule.rule_type.value == 'validation':
            changes = self._apply_validation_preview(df, parsed_rule)
        elif parsed_rule.rule_type.value == 'standardization':
            changes = self._apply_standardization_preview(df, parsed_rule)
        elif parsed_rule.rule_type.value == 'cleaning':
            changes = self._apply_cleaning_preview(df, parsed_rule)
        
        return {
            'changes': changes,
            'total_records': len(df),
            'affected_records': len(changes)
        }
    
    def _apply_validation_preview(self, df: pd.DataFrame, parsed_rule: ParsedRule) -> List[Dict[str, Any]]:
        """Generate preview for validation rules"""
        changes = []
        field = parsed_rule.field
        
        if field == 'weight':
            # Weight validation
            min_weight = parsed_rule.parameters.get('min_weight', 400)
            max_weight = parsed_rule.parameters.get('max_weight', 1500)
            
            for idx, row in df.iterrows():
                weight = row['weight']
                if weight < min_weight or weight > max_weight:
                    changes.append({
                        'row_index': idx,
                        'field': field,
                        'original_value': weight,
                        'suggested_action': 'flag_as_error',
                        'reason': f"Weight {weight} outside valid range ({min_weight}-{max_weight})"
                    })
        
        return changes
    
    def _apply_standardization_preview(self, df: pd.DataFrame, parsed_rule: ParsedRule) -> List[Dict[str, Any]]:
        """Generate preview for standardization rules"""
        changes = []
        field = parsed_rule.field
        
        if field == 'breed':
            # Breed standardization
            for idx, row in df.iterrows():
                breed = row['breed']
                if breed and breed != breed.title():
                    changes.append({
                        'row_index': idx,
                        'field': field,
                        'original_value': breed,
                        'suggested_value': breed.title(),
                        'action': 'standardize_case'
                    })
        
        return changes
    
    def _apply_cleaning_preview(self, df: pd.DataFrame, parsed_rule: ParsedRule) -> List[Dict[str, Any]]:
        """Generate preview for cleaning rules"""
        changes = []
        field = parsed_rule.field
        
        if field == 'birth_date':
            # Date cleaning
            for idx, row in df.iterrows():
                birth_date = row['birth_date']
                if pd.isna(birth_date) or birth_date == '':
                    changes.append({
                        'row_index': idx,
                        'field': field,
                        'original_value': birth_date,
                        'suggested_action': 'remove_record',
                        'reason': 'Missing birth date'
                    })
        
        return changes
    
    def _apply_rule_to_data(self, df: pd.DataFrame, parsed_rule: ParsedRule) -> List[Dict[str, Any]]:
        """Apply rule to actual data and return changes made"""
        changes = []
        
        if parsed_rule.rule_type.value == 'validation':
            changes = self._apply_validation_rule(df, parsed_rule)
        elif parsed_rule.rule_type.value == 'standardization':
            changes = self._apply_standardization_rule(df, parsed_rule)
        elif parsed_rule.rule_type.value == 'cleaning':
            changes = self._apply_cleaning_rule(df, parsed_rule)
        
        return changes
    
    def _apply_validation_rule(self, df: pd.DataFrame, parsed_rule: ParsedRule) -> List[Dict[str, Any]]:
        """Apply validation rule to data"""
        changes = []
        field = parsed_rule.field
        
        if field == 'weight':
            min_weight = parsed_rule.parameters.get('min_weight', 400)
            max_weight = parsed_rule.parameters.get('max_weight', 1500)
            
            # Add validation flag column
            df['weight_validation_flag'] = (df['weight'] < min_weight) | (df['weight'] > max_weight)
            
            flagged_count = df['weight_validation_flag'].sum()
            changes.append({
                'type': 'validation_flag',
                'field': field,
                'records_affected': int(flagged_count),
                'details': f"Flagged {flagged_count} records with weight outside {min_weight}-{max_weight} range"
            })
        
        return changes
    
    def _apply_standardization_rule(self, df: pd.DataFrame, parsed_rule: ParsedRule) -> List[Dict[str, Any]]:
        """Apply standardization rule to data"""
        changes = []
        field = parsed_rule.field
        
        if field == 'breed':
            # Standardize breed names
            original_breeds = df['breed'].copy()
            df['breed'] = df['breed'].str.title()
            
            changed_count = (original_breeds != df['breed']).sum()
            changes.append({
                'type': 'standardization',
                'field': field,
                'records_affected': int(changed_count),
                'details': f"Standardized {changed_count} breed names to proper case"
            })
        
        return changes
    
    def _apply_cleaning_rule(self, df: pd.DataFrame, parsed_rule: ParsedRule) -> List[Dict[str, Any]]:
        """Apply cleaning rule to data"""
        changes = []
        field = parsed_rule.field
        
        if field == 'birth_date':
            # Remove records with missing birth dates
            original_count = len(df)
            df.dropna(subset=['birth_date'], inplace=True)
            removed_count = original_count - len(df)
            
            changes.append({
                'type': 'cleaning',
                'field': field,
                'records_affected': removed_count,
                'details': f"Removed {removed_count} records with missing birth dates"
            })
        
        return changes
    
    def _calculate_quality_metrics(self, df: pd.DataFrame, preview_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate data quality metrics"""
        total_records = len(df)
        affected_records = preview_results['affected_records']
        
        return {
            'total_records': total_records,
            'affected_records': affected_records,
            'quality_score': max(0, 100 - (affected_records / total_records * 100)) if total_records > 0 else 100,
            'completeness': (df.notna().sum() / len(df) * 100).to_dict() if len(df) > 0 else {}
        }
    
    def _create_backup(self, batch_id: str):
        """Create backup of current data state"""
        if batch_id in self.data_cache:
            self.backup_cache[batch_id] = self.data_cache[batch_id].copy()
    
    def _save_batch_info(self, batch_id: str, file_path: str, record_count: int):
        """Save batch information to database"""
        try:
            with SessionLocal() as session:
                batch_info = BatchInfo(
                    batch_id=batch_id,
                    file_path=file_path,
                    record_count=record_count,
                    created_at=datetime.now()
                )
                session.add(batch_info)
                session.commit()
        except Exception as e:
            logger.error(f"Failed to save batch info: {e}")
    
    def _log_operation(self, batch_id: str, parsed_rule: ParsedRule, 
                      changes: List[Dict[str, Any]], client_name: str) -> str:
        """Log operation to database"""
        try:
            operation_id = str(uuid.uuid4())
            with SessionLocal() as session:
                operation_log = OperationLog(
                    operation_id=operation_id,
                    batch_id=batch_id,
                    rule_type=parsed_rule.rule_type.value,
                    rule_description=parsed_rule.description,
                    changes_made=json.dumps(changes),
                    client_name=client_name,
                    created_at=datetime.now()
                )
                session.add(operation_log)
                session.commit()
            return operation_id
        except Exception as e:
            logger.error(f"Failed to log operation: {e}")
            return str(uuid.uuid4())
    
    def _log_rollback(self, batch_id: str, operation_id: str):
        """Log rollback operation"""
        try:
            with SessionLocal() as session:
                rollback_log = OperationLog(
                    operation_id=str(uuid.uuid4()),
                    batch_id=batch_id,
                    rule_type='rollback',
                    rule_description=f'Rollback of operation {operation_id}',
                    changes_made='{}',
                    created_at=datetime.now()
                )
                session.add(rollback_log)
                session.commit()
        except Exception as e:
            logger.error(f"Failed to log rollback: {e}") 