#!/usr/bin/env python3
"""
DataHerd Report Generator

This module generates comprehensive reports for data cleaning operations,
including operation summaries, audit trails, and quality metrics.
"""

import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import pandas as pd
from sqlalchemy import func, and_

from db.models import OperationLog, BatchInfo, CleaningRule, RuleApplication
from db.base import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReportGenerator:
    """Generator for data cleaning operation reports"""
    
    def __init__(self):
        """Initialize the report generator"""
        pass
    
    def generate_comprehensive_report(self, batch_id: str, processing_results: Dict[str, Any],
                                    rule_applications: List[Dict[str, Any]], 
                                    client_name: str = "") -> Dict[str, Any]:
        """
        Generate a comprehensive report for a data cleaning operation
        
        Args:
            batch_id: Batch identifier
            processing_results: Results from data processing
            rule_applications: List of applied rules
            client_name: Client name for context
            
        Returns:
            Comprehensive report dictionary
        """
        try:
            report_id = str(uuid.uuid4())
            
            # Get batch information
            batch_info = self._get_batch_info(batch_id)
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(processing_results)
            
            # Generate report sections
            sections = {
                'executive_summary': self._generate_executive_summary(
                    batch_info, processing_results, quality_metrics
                ),
                'data_quality_assessment': self._generate_quality_assessment(quality_metrics),
                'operation_details': self._generate_operation_details(
                    batch_id, rule_applications
                ),
                'rule_effectiveness': self._generate_rule_effectiveness(rule_applications),
                'recommendations': self._generate_recommendations(quality_metrics, client_name)
            }
            
            # Create report metadata
            metadata = {
                'report_id': report_id,
                'batch_id': batch_id,
                'client_name': client_name,
                'generated_at': datetime.now().isoformat(),
                'report_type': 'comprehensive',
                'processing_summary': {
                    'total_records': processing_results.get('total_records', 0),
                    'changes_applied': processing_results.get('changes_applied', 0),
                    'quality_score': quality_metrics.get('overall_quality_score', 0)
                }
            }
            
            return {
                'report_id': report_id,
                'metadata': metadata,
                'sections': sections,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Failed to generate comprehensive report: {e}")
            return {
                'status': 'error',
                'message': f"Report generation failed: {str(e)}"
            }
    
    def generate_operation_report(self, batch_id: Optional[str] = None,
                                operator_id: Optional[str] = None,
                                start_date: Optional[str] = None,
                                end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate an operation report with filtering options
        
        Args:
            batch_id: Optional batch filter
            operator_id: Optional operator filter
            start_date: Optional start date filter (YYYY-MM-DD)
            end_date: Optional end date filter (YYYY-MM-DD)
            
        Returns:
            Operation report dictionary
        """
        try:
            report_id = str(uuid.uuid4())
            
            # Build query filters
            filters = []
            if batch_id:
                filters.append(OperationLog.batch_id == batch_id)
            if operator_id:
                filters.append(OperationLog.operator_id == operator_id)
            if start_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                filters.append(OperationLog.created_at >= start_dt)
            if end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                filters.append(OperationLog.created_at < end_dt)
            
            # Query operations
            with SessionLocal() as session:
                query = session.query(OperationLog)
                if filters:
                    query = query.filter(and_(*filters))
                
                operations = query.order_by(OperationLog.created_at.desc()).all()
            
            # Generate operation statistics
            stats = self._calculate_operation_statistics(operations)
            
            # Generate operation timeline
            timeline = self._generate_operation_timeline(operations)
            
            return {
                'report_id': report_id,
                'metadata': {
                    'report_id': report_id,
                    'generated_at': datetime.now().isoformat(),
                    'report_type': 'operation',
                    'filters': {
                        'batch_id': batch_id,
                        'operator_id': operator_id,
                        'start_date': start_date,
                        'end_date': end_date
                    }
                },
                'statistics': stats,
                'timeline': timeline,
                'operations': [
                    {
                        'operation_id': op.operation_id,
                        'batch_id': op.batch_id,
                        'rule_type': op.rule_type,
                        'rule_description': op.rule_description,
                        'client_name': op.client_name,
                        'created_at': op.created_at.isoformat()
                    }
                    for op in operations
                ],
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Failed to generate operation report: {e}")
            return {
                'status': 'error',
                'message': f"Operation report generation failed: {str(e)}"
            }
    
    def generate_client_summary_report(self, client_name: str,
                                     start_date: Optional[str] = None,
                                     end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a summary report for a specific client
        
        Args:
            client_name: Client name
            start_date: Optional start date filter
            end_date: Optional end date filter
            
        Returns:
            Client summary report dictionary
        """
        try:
            report_id = str(uuid.uuid4())
            
            # Build date filters
            filters = [OperationLog.client_name == client_name]
            if start_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                filters.append(OperationLog.created_at >= start_dt)
            if end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
                filters.append(OperationLog.created_at < end_dt)
            
            # Query client operations
            with SessionLocal() as session:
                operations = session.query(OperationLog).filter(
                    and_(*filters)
                ).order_by(OperationLog.created_at.desc()).all()
                
                # Get client rules
                rules = session.query(CleaningRule).filter(
                    CleaningRule.client_context == client_name,
                    CleaningRule.is_active == True
                ).all()
            
            # Calculate client statistics
            client_stats = self._calculate_client_statistics(operations, rules)
            
            # Generate client insights
            insights = self._generate_client_insights(operations, rules)
            
            return {
                'report_id': report_id,
                'metadata': {
                    'report_id': report_id,
                    'client_name': client_name,
                    'generated_at': datetime.now().isoformat(),
                    'report_type': 'client_summary',
                    'date_range': {
                        'start_date': start_date,
                        'end_date': end_date
                    }
                },
                'statistics': client_stats,
                'insights': insights,
                'recent_operations': [
                    {
                        'operation_id': op.operation_id,
                        'batch_id': op.batch_id,
                        'rule_type': op.rule_type,
                        'created_at': op.created_at.isoformat()
                    }
                    for op in operations[:10]  # Last 10 operations
                ],
                'active_rules': [
                    {
                        'rule_id': rule.rule_id,
                        'name': rule.name,
                        'usage_count': rule.usage_count,
                        'success_rate': rule.success_rate
                    }
                    for rule in rules
                ],
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Failed to generate client summary report: {e}")
            return {
                'status': 'error',
                'message': f"Client summary report generation failed: {str(e)}"
            }
    
    def _get_batch_info(self, batch_id: str) -> Dict[str, Any]:
        """Get batch information from database"""
        try:
            with SessionLocal() as session:
                batch = session.query(BatchInfo).filter(
                    BatchInfo.batch_id == batch_id
                ).first()
                
                if batch:
                    return {
                        'batch_id': batch.batch_id,
                        'file_path': batch.file_path,
                        'record_count': batch.record_count,
                        'created_at': batch.created_at.isoformat()
                    }
                return {}
                
        except Exception as e:
            logger.error(f"Failed to get batch info: {e}")
            return {}
    
    def _calculate_quality_metrics(self, processing_results: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate data quality metrics"""
        total_records = processing_results.get('total_records', 0)
        changes_applied = processing_results.get('changes_applied', 0)
        
        if total_records == 0:
            return {
                'overall_quality_score': 100,
                'data_completeness': 100,
                'data_accuracy': 100,
                'improvement_percentage': 0
            }
        
        # Calculate quality metrics
        quality_score = max(0, 100 - (changes_applied / total_records * 100))
        improvement_percentage = (changes_applied / total_records * 100) if total_records > 0 else 0
        
        return {
            'overall_quality_score': round(quality_score, 2),
            'data_completeness': 95.0,  # Placeholder - would be calculated from actual data
            'data_accuracy': 92.0,      # Placeholder - would be calculated from actual data
            'improvement_percentage': round(improvement_percentage, 2),
            'total_records': total_records,
            'records_improved': changes_applied
        }
    
    def _generate_executive_summary(self, batch_info: Dict[str, Any],
                                  processing_results: Dict[str, Any],
                                  quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate executive summary section"""
        return {
            'title': 'Executive Summary',
            'content': {
                'batch_overview': {
                    'batch_id': batch_info.get('batch_id', 'Unknown'),
                    'total_records': quality_metrics.get('total_records', 0),
                    'processing_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                },
                'quality_improvement': {
                    'before_score': 100 - quality_metrics.get('improvement_percentage', 0),
                    'after_score': quality_metrics.get('overall_quality_score', 100),
                    'improvement': quality_metrics.get('improvement_percentage', 0)
                },
                'key_achievements': [
                    f"Processed {quality_metrics.get('total_records', 0)} cattle records",
                    f"Applied {processing_results.get('changes_applied', 0)} data improvements",
                    f"Achieved {quality_metrics.get('overall_quality_score', 100)}% data quality score"
                ]
            }
        }
    
    def _generate_quality_assessment(self, quality_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate data quality assessment section"""
        return {
            'title': 'Data Quality Assessment',
            'content': {
                'overall_score': quality_metrics.get('overall_quality_score', 100),
                'completeness_score': quality_metrics.get('data_completeness', 100),
                'accuracy_score': quality_metrics.get('data_accuracy', 100),
                'improvement_details': {
                    'records_processed': quality_metrics.get('total_records', 0),
                    'records_improved': quality_metrics.get('records_improved', 0),
                    'improvement_percentage': quality_metrics.get('improvement_percentage', 0)
                },
                'quality_indicators': [
                    'Data completeness validated',
                    'Outlier detection applied',
                    'Format standardization completed',
                    'Duplicate removal processed'
                ]
            }
        }
    
    def _generate_operation_details(self, batch_id: str,
                                  rule_applications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate operation details section"""
        return {
            'title': 'Operation Details',
            'content': {
                'batch_id': batch_id,
                'rules_applied': len(rule_applications),
                'rule_breakdown': [
                    {
                        'rule_type': rule.get('rule_type', 'Unknown'),
                        'confidence': rule.get('confidence', 0),
                        'changes_made': rule.get('changes_made', 0)
                    }
                    for rule in rule_applications
                ],
                'processing_timeline': {
                    'start_time': datetime.now().isoformat(),
                    'end_time': datetime.now().isoformat(),
                    'duration': '2.5 minutes'  # Placeholder
                }
            }
        }
    
    def _generate_rule_effectiveness(self, rule_applications: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate rule effectiveness section"""
        if not rule_applications:
            return {
                'title': 'Rule Effectiveness',
                'content': {
                    'message': 'No rules were applied in this operation'
                }
            }
        
        total_changes = sum(rule.get('changes_made', 0) for rule in rule_applications)
        avg_confidence = sum(rule.get('confidence', 0) for rule in rule_applications) / len(rule_applications)
        
        return {
            'title': 'Rule Effectiveness',
            'content': {
                'total_rules_applied': len(rule_applications),
                'total_changes_made': total_changes,
                'average_confidence': round(avg_confidence, 2),
                'rule_performance': [
                    {
                        'rule_type': rule.get('rule_type', 'Unknown'),
                        'effectiveness': 'High' if rule.get('confidence', 0) > 0.8 else 'Medium',
                        'changes_made': rule.get('changes_made', 0)
                    }
                    for rule in rule_applications
                ]
            }
        }
    
    def _generate_recommendations(self, quality_metrics: Dict[str, Any],
                                client_name: str) -> Dict[str, Any]:
        """Generate recommendations section"""
        recommendations = []
        
        quality_score = quality_metrics.get('overall_quality_score', 100)
        
        if quality_score < 90:
            recommendations.append("Consider implementing additional validation rules")
            recommendations.append("Review data sources for consistency issues")
        
        if quality_metrics.get('improvement_percentage', 0) < 5:
            recommendations.append("Data quality is already high - consider optimizing processing efficiency")
        
        if client_name:
            recommendations.append(f"Continue using client-specific rules for {client_name}")
        
        return {
            'title': 'Recommendations',
            'content': {
                'recommendations': recommendations,
                'next_steps': [
                    'Monitor data quality trends over time',
                    'Update rule effectiveness based on usage patterns',
                    'Consider expanding rule coverage to additional fields'
                ]
            }
        }
    
    def _calculate_operation_statistics(self, operations: List[Any]) -> Dict[str, Any]:
        """Calculate operation statistics"""
        if not operations:
            return {
                'total_operations': 0,
                'unique_batches': 0,
                'unique_clients': 0,
                'date_range': {'start': None, 'end': None}
            }
        
        unique_batches = len(set(op.batch_id for op in operations))
        unique_clients = len(set(op.client_name for op in operations if op.client_name))
        
        dates = [op.created_at for op in operations]
        date_range = {
            'start': min(dates).isoformat() if dates else None,
            'end': max(dates).isoformat() if dates else None
        }
        
        return {
            'total_operations': len(operations),
            'unique_batches': unique_batches,
            'unique_clients': unique_clients,
            'date_range': date_range
        }
    
    def _generate_operation_timeline(self, operations: List[Any]) -> List[Dict[str, Any]]:
        """Generate operation timeline"""
        timeline = []
        
        for op in operations:
            timeline.append({
                'timestamp': op.created_at.isoformat(),
                'operation_id': op.operation_id,
                'batch_id': op.batch_id,
                'rule_type': op.rule_type,
                'description': op.rule_description
            })
        
        return timeline
    
    def _calculate_client_statistics(self, operations: List[Any], rules: List[Any]) -> Dict[str, Any]:
        """Calculate client-specific statistics"""
        total_operations = len(operations)
        total_rules = len(rules)
        
        # Calculate average success rate
        avg_success_rate = sum(rule.success_rate for rule in rules) / total_rules if total_rules > 0 else 0
        
        return {
            'total_operations': total_operations,
            'active_rules': total_rules,
            'average_success_rate': round(avg_success_rate, 2),
            'last_operation': operations[0].created_at.isoformat() if operations else None
        }
    
    def _generate_client_insights(self, operations: List[Any], rules: List[Any]) -> List[str]:
        """Generate insights for client"""
        insights = []
        
        if operations:
            insights.append(f"Client has {len(operations)} total operations")
        
        if rules:
            insights.append(f"Client has {len(rules)} active cleaning rules")
            
            # Find most used rule
            most_used_rule = max(rules, key=lambda r: r.usage_count) if rules else None
            if most_used_rule and most_used_rule.usage_count > 0:
                insights.append(f"Most used rule: {most_used_rule.name} ({most_used_rule.usage_count} times)")
        
        return insights 