#!/usr/bin/env python3
"""
DataHerd Rule Manager

This module manages the lifecycle of cleaning rules including storage,
retrieval, and client-specific customization.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from .nlp_processor import ParsedRule
from db.models import CleaningRule, RuleApplication, ClientTemplate
from db.base import SessionLocal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RuleManager:
    """Manager for cleaning rules and templates"""
    
    def __init__(self):
        """Initialize the rule manager"""
        pass
    
    def save_rule(self, parsed_rule: ParsedRule, rule_name: str, 
                  client_name: str = "", is_permanent: bool = False) -> str:
        """
        Save a cleaning rule to the database
        
        Args:
            parsed_rule: Parsed rule object
            rule_name: Human-readable name for the rule
            client_name: Client name for context
            is_permanent: Whether this is a permanent system rule
            
        Returns:
            Rule ID string
        """
        try:
            rule_id = str(uuid.uuid4())
            
            with SessionLocal() as session:
                rule = CleaningRule(
                    rule_id=rule_id,
                    name=rule_name,
                    description=parsed_rule.description,
                    rule_type=parsed_rule.rule_type.value,
                    field=parsed_rule.field,
                    condition=parsed_rule.condition,
                    action=parsed_rule.action,
                    parameters=json.dumps(parsed_rule.parameters),
                    confidence=parsed_rule.confidence,
                    client_context=client_name,
                    is_permanent=is_permanent,
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                
                session.add(rule)
                session.commit()
                
                logger.info(f"Rule saved successfully: {rule_id}")
                return rule_id
                
        except Exception as e:
            logger.error(f"Failed to save rule: {e}")
            raise
    
    def get_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a rule by ID
        
        Args:
            rule_id: Rule identifier
            
        Returns:
            Rule dictionary or None if not found
        """
        try:
            with SessionLocal() as session:
                rule = session.query(CleaningRule).filter(
                    CleaningRule.rule_id == rule_id
                ).first()
                
                if rule:
                    return {
                        'rule_id': rule.rule_id,
                        'name': rule.name,
                        'description': rule.description,
                        'rule_type': rule.rule_type,
                        'field': rule.field,
                        'condition': rule.condition,
                        'action': rule.action,
                        'parameters': json.loads(rule.parameters),
                        'confidence': rule.confidence,
                        'client_context': rule.client_context,
                        'is_permanent': rule.is_permanent,
                        'is_active': rule.is_active,
                        'usage_count': rule.usage_count,
                        'success_rate': rule.success_rate,
                        'created_at': rule.created_at.isoformat(),
                        'updated_at': rule.updated_at.isoformat()
                    }
                return None
                
        except Exception as e:
            logger.error(f"Failed to retrieve rule: {e}")
            return None
    
    def get_client_rules(self, client_name: str) -> List[Dict[str, Any]]:
        """
        Get all rules for a specific client
        
        Args:
            client_name: Client name
            
        Returns:
            List of rule dictionaries
        """
        try:
            with SessionLocal() as session:
                rules = session.query(CleaningRule).filter(
                    CleaningRule.client_context == client_name,
                    CleaningRule.is_active == True
                ).all()
                
                return [
                    {
                        'rule_id': rule.rule_id,
                        'name': rule.name,
                        'description': rule.description,
                        'rule_type': rule.rule_type,
                        'field': rule.field,
                        'confidence': rule.confidence,
                        'usage_count': rule.usage_count,
                        'success_rate': rule.success_rate,
                        'created_at': rule.created_at.isoformat()
                    }
                    for rule in rules
                ]
                
        except Exception as e:
            logger.error(f"Failed to retrieve client rules: {e}")
            return []
    
    def get_permanent_rules(self) -> List[Dict[str, Any]]:
        """
        Get all permanent system rules
        
        Returns:
            List of permanent rule dictionaries
        """
        try:
            with SessionLocal() as session:
                rules = session.query(CleaningRule).filter(
                    CleaningRule.is_permanent == True,
                    CleaningRule.is_active == True
                ).all()
                
                return [
                    {
                        'rule_id': rule.rule_id,
                        'name': rule.name,
                        'description': rule.description,
                        'rule_type': rule.rule_type,
                        'field': rule.field,
                        'confidence': rule.confidence,
                        'usage_count': rule.usage_count,
                        'success_rate': rule.success_rate,
                        'created_at': rule.created_at.isoformat()
                    }
                    for rule in rules
                ]
                
        except Exception as e:
            logger.error(f"Failed to retrieve permanent rules: {e}")
            return []
    
    def update_permanent_rule(self, rule_id: str, new_description: str) -> bool:
        """
        Update a permanent rule description
        
        Args:
            rule_id: Rule identifier
            new_description: New rule description
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with SessionLocal() as session:
                rule = session.query(CleaningRule).filter(
                    CleaningRule.rule_id == rule_id,
                    CleaningRule.is_permanent == True
                ).first()
                
                if rule:
                    rule.description = new_description
                    rule.updated_at = datetime.now()
                    session.commit()
                    logger.info(f"Permanent rule updated: {rule_id}")
                    return True
                else:
                    logger.warning(f"Permanent rule not found: {rule_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to update permanent rule: {e}")
            return False
    
    def deactivate_rule(self, rule_id: str) -> bool:
        """
        Deactivate a rule (soft delete)
        
        Args:
            rule_id: Rule identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with SessionLocal() as session:
                rule = session.query(CleaningRule).filter(
                    CleaningRule.rule_id == rule_id
                ).first()
                
                if rule:
                    rule.is_active = False
                    rule.updated_at = datetime.now()
                    session.commit()
                    logger.info(f"Rule deactivated: {rule_id}")
                    return True
                else:
                    logger.warning(f"Rule not found: {rule_id}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to deactivate rule: {e}")
            return False
    
    def track_rule_usage(self, rule_id: str, batch_id: str, 
                        success: bool, changes_made: int) -> bool:
        """
        Track rule usage and success rate
        
        Args:
            rule_id: Rule identifier
            batch_id: Batch identifier
            success: Whether the rule application was successful
            changes_made: Number of changes made
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with SessionLocal() as session:
                # Log rule application
                application = RuleApplication(
                    application_id=str(uuid.uuid4()),
                    rule_id=rule_id,
                    batch_id=batch_id,
                    applied_at=datetime.now(),
                    success=success,
                    changes_made=changes_made
                )
                session.add(application)
                
                # Update rule statistics
                rule = session.query(CleaningRule).filter(
                    CleaningRule.rule_id == rule_id
                ).first()
                
                if rule:
                    rule.usage_count += 1
                    
                    # Calculate success rate
                    total_applications = session.query(RuleApplication).filter(
                        RuleApplication.rule_id == rule_id
                    ).count()
                    
                    successful_applications = session.query(RuleApplication).filter(
                        RuleApplication.rule_id == rule_id,
                        RuleApplication.success == True
                    ).count()
                    
                    rule.success_rate = (successful_applications / total_applications * 100) if total_applications > 0 else 0
                    rule.updated_at = datetime.now()
                
                session.commit()
                return True
                
        except Exception as e:
            logger.error(f"Failed to track rule usage: {e}")
            return False
    
    def create_template(self, client_name: str, template_name: str, 
                       rule_ids: List[str]) -> str:
        """
        Create a rule template for a client
        
        Args:
            client_name: Client name
            template_name: Template name
            rule_ids: List of rule IDs to include in template
            
        Returns:
            Template ID string
        """
        try:
            template_id = str(uuid.uuid4())
            
            with SessionLocal() as session:
                template = ClientTemplate(
                    template_id=template_id,
                    client_name=client_name,
                    template_name=template_name,
                    template_rules=json.dumps(rule_ids),
                    created_at=datetime.now(),
                    is_active=True
                )
                
                session.add(template)
                session.commit()
                
                logger.info(f"Template created: {template_id}")
                return template_id
                
        except Exception as e:
            logger.error(f"Failed to create template: {e}")
            raise
    
    def get_client_templates(self, client_name: str) -> List[Dict[str, Any]]:
        """
        Get all templates for a client
        
        Args:
            client_name: Client name
            
        Returns:
            List of template dictionaries
        """
        try:
            with SessionLocal() as session:
                templates = session.query(ClientTemplate).filter(
                    ClientTemplate.client_name == client_name,
                    ClientTemplate.is_active == True
                ).all()
                
                return [
                    {
                        'template_id': template.template_id,
                        'template_name': template.template_name,
                        'rule_count': len(json.loads(template.template_rules)),
                        'created_at': template.created_at.isoformat()
                    }
                    for template in templates
                ]
                
        except Exception as e:
            logger.error(f"Failed to retrieve client templates: {e}")
            return []
    
    def apply_template(self, template_id: str, batch_id: str) -> List[str]:
        """
        Apply a template to a batch
        
        Args:
            template_id: Template identifier
            batch_id: Batch identifier
            
        Returns:
            List of applied rule IDs
        """
        try:
            with SessionLocal() as session:
                template = session.query(ClientTemplate).filter(
                    ClientTemplate.template_id == template_id,
                    ClientTemplate.is_active == True
                ).first()
                
                if not template:
                    logger.warning(f"Template not found: {template_id}")
                    return []
                
                rule_ids = json.loads(template.template_rules)
                applied_rules = []
                
                for rule_id in rule_ids:
                    # Track usage for each rule in template
                    self.track_rule_usage(rule_id, batch_id, True, 0)
                    applied_rules.append(rule_id)
                
                logger.info(f"Template applied: {template_id} to batch {batch_id}")
                return applied_rules
                
        except Exception as e:
            logger.error(f"Failed to apply template: {e}")
            return []
    
    def get_rule_statistics(self, client_name: str = None) -> Dict[str, Any]:
        """
        Get rule usage statistics
        
        Args:
            client_name: Optional client filter
            
        Returns:
            Statistics dictionary
        """
        try:
            with SessionLocal() as session:
                query = session.query(CleaningRule)
                
                if client_name:
                    query = query.filter(CleaningRule.client_context == client_name)
                
                rules = query.all()
                
                total_rules = len(rules)
                active_rules = len([r for r in rules if r.is_active])
                permanent_rules = len([r for r in rules if r.is_permanent])
                
                avg_usage = sum(r.usage_count for r in rules) / total_rules if total_rules > 0 else 0
                avg_success_rate = sum(r.success_rate for r in rules) / total_rules if total_rules > 0 else 0
                
                return {
                    'total_rules': total_rules,
                    'active_rules': active_rules,
                    'permanent_rules': permanent_rules,
                    'average_usage': round(avg_usage, 2),
                    'average_success_rate': round(avg_success_rate, 2)
                }
                
        except Exception as e:
            logger.error(f"Failed to get rule statistics: {e}")
            return {} 