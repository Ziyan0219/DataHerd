"""
DataHerd Data Processor
Handles data cleaning operations for cattle lot management with NLP integration
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import re
import json
import uuid
from .nlp_processor import NLPProcessor, ParsedRule, RuleType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataProcessor:
    """Main data processing class for cattle data cleaning with NLP support"""
    
    def __init__(self):
        self.processed_batches = {}
        self.cleaning_history = []
        self.nlp_processor = NLPProcessor()
        self.preview_cache = {}
        self.operation_logs = []
        
    def load_data(self, file_path: str, batch_id: str) -> pd.DataFrame:
        """Load data from file"""
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            
            logger.info(f"Loaded {len(df)} records for batch {batch_id}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading data: {str(e)}")
            raise
    
    def process_natural_language_rules(self, rule_text: str, client_context: str = "") -> List[ParsedRule]:
        """
        Process natural language rules using NLP
        
        Args:
            rule_text: Natural language description of cleaning rules
            client_context: Additional context about the client
            
        Returns:
            List of parsed rules
        """
        try:
            parsed_rules = self.nlp_processor.parse_natural_language_rule(rule_text, client_context)
            logger.info(f"Processed {len(parsed_rules)} rules from natural language input")
            return parsed_rules
        except Exception as e:
            logger.error(f"Error processing natural language rules: {str(e)}")
            raise
    
    def preview_cleaning_operation(self, batch_id: str, natural_language_rules: str, client_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Preview data cleaning operation without applying changes.
        
        Args:
            batch_id: Identifier for the data batch
            natural_language_rules: Natural language description of cleaning rules
            client_name: Optional client name for specific rule adjustments
            
        Returns:
            Dictionary containing preview results
        """
        try:
            # Generate sample data for preview (in real implementation, load actual data)
            df = self._generate_sample_data()
            
            # Process natural language rules
            parsed_rules = self.process_natural_language_rules(natural_language_rules, client_name or "")
            
            # Generate preview
            preview_results = self.preview_changes(df, parsed_rules, batch_id)
            
            return preview_results
            
        except Exception as e:
            logger.error(f"Error in preview_cleaning_operation: {str(e)}")
            raise Exception(f"Preview operation failed: {str(e)}")
    
    def preview_changes(self, df: pd.DataFrame, parsed_rules: List[ParsedRule], batch_id: str) -> Dict[str, Any]:
        """
        Preview changes that would be made by applying rules
        
        Args:
            df: Input DataFrame
            parsed_rules: List of parsed rules
            batch_id: Unique identifier for this batch
            
        Returns:
            Dictionary with preview information
        """
        preview_results = {
            'batch_id': batch_id,
            'original_count': len(df),
            'rules_applied': len(parsed_rules),
            'potential_changes': [],
            'issues_found': [],
            'summary': {},
            'confidence_scores': []
        }
        
        # Apply each rule and collect potential changes
        for rule in parsed_rules:
            try:
                if rule.rule_type == RuleType.VALIDATION:
                    issues = self._preview_validation(df, rule)
                    preview_results['issues_found'].extend(issues)
                
                elif rule.rule_type == RuleType.STANDARDIZATION:
                    changes = self._preview_standardization(df, rule)
                    preview_results['potential_changes'].extend(changes)
                
                elif rule.rule_type == RuleType.CLEANING:
                    changes = self._preview_cleaning(df, rule)
                    preview_results['potential_changes'].extend(changes)
                
                elif rule.rule_type == RuleType.ESTIMATION:
                    changes = self._preview_estimation(df, rule)
                    preview_results['potential_changes'].extend(changes)
                
                preview_results['confidence_scores'].append({
                    'rule': rule.description,
                    'confidence': rule.confidence
                })
                
            except Exception as e:
                logger.error(f"Error previewing rule {rule.description}: {str(e)}")
                continue
        
        # Generate summary
        preview_results['summary'] = {
            'total_issues': len(preview_results['issues_found']),
            'total_changes': len(preview_results['potential_changes']),
            'avg_confidence': np.mean([score['confidence'] for score in preview_results['confidence_scores']]) if preview_results['confidence_scores'] else 0,
            'high_confidence_changes': len([c for c in preview_results['potential_changes'] if c.get('confidence', 0) > 0.8]),
            'rules_processed': len(parsed_rules)
        }
        
        # Cache preview for later application
        self.preview_cache[batch_id] = {
            'df': df.copy(),
            'rules': parsed_rules,
            'preview': preview_results,
            'timestamp': datetime.now()
        }
        
        return preview_results
    
    def apply_cleaning_rules(self, batch_id: str, cleaning_rules: str, apply_permanently: bool = False) -> Dict[str, Any]:
        """
        Apply cleaning rules to the specified batch.
        
        Args:
            batch_id: Identifier for the data batch
            cleaning_rules: Natural language description of cleaning rules
            apply_permanently: Whether to save changes permanently
            
        Returns:
            Dictionary containing operation results
        """
        try:
            # Generate operation log ID
            operation_id = str(uuid.uuid4())
            
            # If we have cached preview data, use it
            if batch_id in self.preview_cache:
                results = self.apply_changes(batch_id)
            else:
                # Generate sample data and process rules
                df = self._generate_sample_data()
                parsed_rules = self.process_natural_language_rules(cleaning_rules)
                preview = self.preview_changes(df, parsed_rules, batch_id)
                results = self.apply_changes(batch_id)
            
            # Create operation log
            operation_log = {
                "operation_id": operation_id,
                "batch_id": batch_id,
                "rules_applied": cleaning_rules,
                "permanent": apply_permanently,
                "timestamp": datetime.now().isoformat(),
                "status": "completed",
                "changes_made": {
                    "flagged_records": len([c for c in results['changes_applied'] if c.get('rule_type') == 'validation']),
                    "deleted_records": len([c for c in results['changes_applied'] if c.get('suggested') == 'remove']),
                    "modified_records": len([c for c in results['changes_applied'] if c.get('rule_type') in ['standardization', 'estimation']])
                }
            }
            
            # Store operation log for potential rollback
            self.operation_logs.append(operation_log)
            
            return {
                "operation_id": operation_id,
                "status": "success",
                "message": "Data cleaning completed successfully",
                "changes_summary": operation_log["changes_made"],
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error in apply_cleaning_rules: {str(e)}")
            raise Exception(f"Data cleaning failed: {str(e)}")
    
    def apply_changes(self, batch_id: str, approved_changes: List[str] = None) -> Dict[str, Any]:
        """
        Apply approved changes from preview
        
        Args:
            batch_id: Batch identifier
            approved_changes: List of change IDs to apply (None = apply all)
            
        Returns:
            Results of applying changes
        """
        if batch_id not in self.preview_cache:
            raise ValueError(f"No preview found for batch {batch_id}")
        
        cached_data = self.preview_cache[batch_id]
        df = cached_data['df'].copy()
        rules = cached_data['rules']
        preview = cached_data['preview']
        
        results = {
            'batch_id': batch_id,
            'original_count': len(df),
            'changes_applied': [],
            'issues_resolved': [],
            'final_data': df,
            'summary': {}
        }
        
        # Apply changes
        changes_to_apply = preview['potential_changes']
        if approved_changes:
            changes_to_apply = [c for c in changes_to_apply if c.get('id') in approved_changes]
        
        for change in changes_to_apply:
            try:
                self._apply_single_change(df, change)
                results['changes_applied'].append(change)
            except Exception as e:
                logger.error(f"Error applying change: {str(e)}")
                continue
        
        # Update final data
        results['final_data'] = df
        results['final_count'] = len(df)
        
        # Generate summary
        results['summary'] = {
            'changes_applied': len(results['changes_applied']),
            'records_modified': len(set(c.get('row_id') for c in results['changes_applied'])),
            'final_count': len(df),
            'data_quality_improvement': self._calculate_quality_improvement(preview, results)
        }
        
        # Store in processing history
        self.cleaning_history.append({
            'batch_id': batch_id,
            'timestamp': datetime.now(),
            'rules_applied': len(rules),
            'changes_made': len(results['changes_applied']),
            'final_count': len(df)
        })
        
        return results
    
    def rollback_operation(self, batch_id: str, operation_log_id: str) -> Dict[str, Any]:
        """
        Rollback a previous data cleaning operation.
        
        Args:
            batch_id: Identifier for the data batch
            operation_log_id: ID of the operation to rollback
            
        Returns:
            Dictionary containing rollback status
        """
        try:
            # Find the operation log
            operation_log = None
            for log in self.operation_logs:
                if log["operation_id"] == operation_log_id and log["batch_id"] == batch_id:
                    operation_log = log
                    break
            
            if not operation_log:
                raise Exception(f"Operation log {operation_log_id} not found for batch {batch_id}")
            
            # Use cached original data if available
            if batch_id in self.preview_cache:
                rollback_data = self.rollback_changes(batch_id)
                
                rollback_result = {
                    "operation_id": operation_log_id,
                    "batch_id": batch_id,
                    "rollback_status": "success",
                    "message": "Operation successfully rolled back",
                    "original_operation": {
                        "timestamp": operation_log["timestamp"],
                        "rules": operation_log["rules_applied"]
                    },
                    "rollback_timestamp": datetime.now().isoformat(),
                    "rollback_data": rollback_data
                }
                
                # Mark operation as rolled back
                operation_log["status"] = "rolled_back"
                operation_log["rollback_timestamp"] = datetime.now().isoformat()
                
                return rollback_result
            else:
                raise Exception("No cached data available for rollback")
            
        except Exception as e:
            logger.error(f"Error in rollback_operation: {str(e)}")
            raise Exception(f"Rollback failed: {str(e)}")
    
    def rollback_changes(self, batch_id: str) -> Dict[str, Any]:
        """
        Rollback changes for a specific batch
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Original data and rollback status
        """
        if batch_id not in self.preview_cache:
            raise ValueError(f"No cached data found for batch {batch_id}")
        
        cached_data = self.preview_cache[batch_id]
        original_df = cached_data['df'].copy()
        
        return {
            'batch_id': batch_id,
            'status': 'rolled_back',
            'original_data': original_df,
            'rollback_timestamp': datetime.now()
        }
    
    def get_operation_history(self, batch_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get operation history for a specific batch or all batches.
        
        Args:
            batch_id: Optional batch ID to filter results
            
        Returns:
            List of operation logs
        """
        if batch_id:
            return [log for log in self.operation_logs if log["batch_id"] == batch_id]
        return self.operation_logs.copy()
    
    def _generate_sample_data(self) -> pd.DataFrame:
        """Generate sample cattle data for testing"""
        np.random.seed(42)
        
        sample_data = {
            'lot_id': [f'LOT{str(i).zfill(3)}' for i in range(1, 101)],
            'weight': np.random.normal(850, 200, 100).astype(int),
            'breed': np.random.choice(['Angus', 'angus', 'Hereford', 'hereford', 'Holstein', 'holstein'], 100),
            'birth_date': pd.date_range('2022-01-01', '2024-12-31', periods=100).strftime('%Y-%m-%d')
        }
        
        # Introduce some data quality issues
        sample_data['weight'][5] = 45  # Too low
        sample_data['weight'][15] = 2000  # Too high
        sample_data['breed'][10] = 'angus'  # Wrong case
        sample_data['breed'][20] = 'HEREFORD'  # Wrong case
        sample_data['birth_date'][25] = 'invalid'  # Invalid date
        sample_data['lot_id'][30] = sample_data['lot_id'][29]  # Duplicate
        
        return pd.DataFrame(sample_data)
    
    def _preview_validation(self, df: pd.DataFrame, rule: ParsedRule) -> List[Dict]:
        """Preview validation rule"""
        issues = []
        
        if rule.field == 'weight':
            min_weight = rule.parameters.get('min_weight', 400)
            max_weight = rule.parameters.get('max_weight', 1500)
            
            for idx, row in df.iterrows():
                weight = row.get(rule.field)
                if pd.isna(weight) or weight < min_weight or weight > max_weight:
                    issues.append({
                        'id': f"validation_{rule.field}_{idx}",
                        'row_id': idx,
                        'field': rule.field,
                        'value': weight,
                        'issue': f'Weight outside normal range ({min_weight}-{max_weight} lbs)',
                        'confidence': rule.confidence,
                        'rule_type': 'validation'
                    })
        
        elif rule.field == 'birth_date':
            current_date = pd.Timestamp.now()
            max_age_years = rule.parameters.get('max_age_years', 3)
            
            for idx, row in df.iterrows():
                birth_date = row.get(rule.field)
                try:
                    date_obj = pd.to_datetime(birth_date)
                    age_years = (current_date - date_obj).days / 365.25
                    
                    if age_years < 0 or age_years > max_age_years:
                        issues.append({
                            'id': f"validation_{rule.field}_{idx}",
                            'row_id': idx,
                            'field': rule.field,
                            'value': birth_date,
                            'issue': f'Unrealistic age: {age_years:.1f} years',
                            'confidence': rule.confidence,
                            'rule_type': 'validation'
                        })
                except:
                    issues.append({
                        'id': f"validation_{rule.field}_{idx}",
                        'row_id': idx,
                        'field': rule.field,
                        'value': birth_date,
                        'issue': 'Invalid date format',
                        'confidence': rule.confidence,
                        'rule_type': 'validation'
                    })
        
        return issues
    
    def _preview_standardization(self, df: pd.DataFrame, rule: ParsedRule) -> List[Dict]:
        """Preview standardization rule"""
        changes = []
        
        if rule.field == 'breed':
            breed_mapping = {
                'angus': 'Angus',
                'hereford': 'Hereford',
                'holstein': 'Holstein',
                'charolais': 'Charolais',
                'simmental': 'Simmental',
                'limousin': 'Limousin'
            }
            
            for idx, row in df.iterrows():
                original_breed = row.get(rule.field)
                if pd.notna(original_breed):
                    standardized = breed_mapping.get(original_breed.lower(), original_breed.title())
                    if standardized != original_breed:
                        changes.append({
                            'id': f"standardization_{rule.field}_{idx}",
                            'row_id': idx,
                            'field': rule.field,
                            'original': original_breed,
                            'suggested': standardized,
                            'reason': 'Breed name standardization',
                            'confidence': rule.confidence,
                            'rule_type': 'standardization'
                        })
        
        return changes
    
    def _preview_cleaning(self, df: pd.DataFrame, rule: ParsedRule) -> List[Dict]:
        """Preview cleaning rule"""
        changes = []
        
        if 'duplicate' in rule.action.lower():
            based_on = rule.parameters.get('based_on', ['lot_id'])
            keep = rule.parameters.get('keep', 'first')
            
            duplicates = df.duplicated(subset=based_on, keep=keep)
            duplicate_indices = df[duplicates].index.tolist()
            
            for idx in duplicate_indices:
                changes.append({
                    'id': f"cleaning_duplicate_{idx}",
                    'row_id': idx,
                    'field': 'record',
                    'original': 'duplicate_record',
                    'suggested': 'remove',
                    'reason': f'Duplicate based on {", ".join(based_on)}',
                    'confidence': rule.confidence,
                    'rule_type': 'cleaning'
                })
        
        return changes
    
    def _preview_estimation(self, df: pd.DataFrame, rule: ParsedRule) -> List[Dict]:
        """Preview estimation rule"""
        changes = []
        
        # Simple estimation based on available data
        valid_values = df[df[rule.field].notna()][rule.field]
        if len(valid_values) > 0:
            if rule.field == 'weight':
                estimated_value = valid_values.median()
            else:
                estimated_value = valid_values.mode().iloc[0] if len(valid_values.mode()) > 0 else valid_values.median()
            
            for idx, row in df.iterrows():
                if pd.isna(row.get(rule.field)):
                    changes.append({
                        'id': f"estimation_{rule.field}_{idx}",
                        'row_id': idx,
                        'field': rule.field,
                        'original': None,
                        'suggested': estimated_value,
                        'reason': 'Estimated based on similar records',
                        'confidence': rule.confidence * 0.7,  # Lower confidence for estimations
                        'rule_type': 'estimation'
                    })
        
        return changes
    
    def _apply_single_change(self, df: pd.DataFrame, change: Dict):
        """Apply a single change to the DataFrame"""
        row_id = change['row_id']
        field = change['field']
        
        if change['rule_type'] == 'standardization':
            df.at[row_id, field] = change['suggested']
        elif change['rule_type'] == 'cleaning' and change['suggested'] == 'remove':
            df.drop(row_id, inplace=True)
        elif change['rule_type'] == 'estimation':
            df.at[row_id, field] = change['suggested']
    
    def _calculate_quality_improvement(self, preview: Dict, results: Dict) -> float:
        """Calculate data quality improvement percentage"""
        total_issues = preview['summary']['total_issues']
        changes_applied = len(results['changes_applied'])
        
        if total_issues == 0:
            return 100.0
        
        improvement = (changes_applied / total_issues) * 100
        return min(improvement, 100.0)
    
    def get_processing_history(self) -> List[Dict]:
        """Get history of all processing operations"""
        return self.cleaning_history

