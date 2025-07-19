"""
Rule Manager Module for DataHerd

This module handles the management of cleaning rules for cattle data processing.
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class RuleManager:
    """
    Manages cleaning rules for cattle data processing operations.
    """
    
    def __init__(self):
        """Initialize the RuleManager."""
        self.client_rules = {}
        self.permanent_rules = {}
        
    def save_rule(self, client_name: str, natural_language_rule: str, is_permanent: bool = False) -> Dict[str, Any]:
        """
        Save a new cleaning rule for a client.
        
        Args:
            client_name: Name of the client
            natural_language_rule: Natural language description of the rule
            is_permanent: Whether this rule should be saved as a permanent rule
            
        Returns:
            Dictionary containing save operation result
        """
        try:
            rule_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            rule_data = {
                "rule_id": rule_id,
                "client_name": client_name,
                "natural_language_rule": natural_language_rule,
                "is_permanent": is_permanent,
                "created_at": timestamp,
                "status": "active"
            }
            
            # Save to client-specific rules
            if client_name not in self.client_rules:
                self.client_rules[client_name] = []
            self.client_rules[client_name].append(rule_data)
            
            # If permanent, also save to permanent rules
            if is_permanent:
                self.permanent_rules[rule_id] = rule_data
            
            return {
                "status": 200,
                "data": {
                    "message": "Rule saved successfully",
                    "rule_id": rule_id,
                    "client_name": client_name,
                    "is_permanent": is_permanent
                }
            }
            
        except Exception as e:
            logger.error(f"Error in save_rule: {str(e)}")
            return {
                "status": 500,
                "data": {
                    "message": f"Failed to save rule: {str(e)}"
                }
            }
    
    def update_permanent_rule(self, rule_id: str, new_natural_language_rule: str) -> Dict[str, Any]:
        """
        Update an existing permanent cleaning rule.
        
        Args:
            rule_id: ID of the rule to update
            new_natural_language_rule: New natural language description
            
        Returns:
            Dictionary containing update operation result
        """
        try:
            if rule_id not in self.permanent_rules:
                return {
                    "status": 404,
                    "data": {
                        "message": f"Permanent rule {rule_id} not found"
                    }
                }
            
            # Update the rule
            self.permanent_rules[rule_id]["natural_language_rule"] = new_natural_language_rule
            self.permanent_rules[rule_id]["updated_at"] = datetime.now().isoformat()
            
            # Also update in client rules if it exists
            client_name = self.permanent_rules[rule_id]["client_name"]
            if client_name in self.client_rules:
                for rule in self.client_rules[client_name]:
                    if rule["rule_id"] == rule_id:
                        rule["natural_language_rule"] = new_natural_language_rule
                        rule["updated_at"] = datetime.now().isoformat()
                        break
            
            return {
                "status": 200,
                "data": {
                    "message": "Permanent rule updated successfully",
                    "rule_id": rule_id,
                    "updated_rule": new_natural_language_rule
                }
            }
            
        except Exception as e:
            logger.error(f"Error in update_permanent_rule: {str(e)}")
            return {
                "status": 500,
                "data": {
                    "message": f"Failed to update permanent rule: {str(e)}"
                }
            }
    
    def get_rules_for_client(self, client_name: str) -> List[Dict[str, Any]]:
        """
        Get all cleaning rules for a specific client.
        
        Args:
            client_name: Name of the client
            
        Returns:
            List of rules for the client
        """
        try:
            client_rules = self.client_rules.get(client_name, [])
            
            # Also include permanent rules that might apply
            applicable_permanent_rules = []
            for rule_id, rule_data in self.permanent_rules.items():
                if rule_data["status"] == "active":
                    applicable_permanent_rules.append(rule_data)
            
            return {
                "client_specific_rules": client_rules,
                "applicable_permanent_rules": applicable_permanent_rules,
                "total_rules": len(client_rules) + len(applicable_permanent_rules)
            }
            
        except Exception as e:
            logger.error(f"Error in get_rules_for_client: {str(e)}")
            return {
                "client_specific_rules": [],
                "applicable_permanent_rules": [],
                "total_rules": 0,
                "error": str(e)
            }
    
    def get_permanent_rules(self) -> List[Dict[str, Any]]:
        """
        Get all permanent cleaning rules.
        
        Returns:
            List of permanent rules
        """
        return [rule for rule in self.permanent_rules.values() if rule["status"] == "active"]
    
    def delete_rule(self, rule_id: str, client_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Delete a cleaning rule.
        
        Args:
            rule_id: ID of the rule to delete
            client_name: Optional client name for client-specific rules
            
        Returns:
            Dictionary containing delete operation result
        """
        try:
            deleted = False
            
            # Check permanent rules
            if rule_id in self.permanent_rules:
                self.permanent_rules[rule_id]["status"] = "deleted"
                self.permanent_rules[rule_id]["deleted_at"] = datetime.now().isoformat()
                deleted = True
            
            # Check client-specific rules
            if client_name and client_name in self.client_rules:
                for rule in self.client_rules[client_name]:
                    if rule["rule_id"] == rule_id:
                        rule["status"] = "deleted"
                        rule["deleted_at"] = datetime.now().isoformat()
                        deleted = True
                        break
            
            if deleted:
                return {
                    "status": 200,
                    "data": {
                        "message": "Rule deleted successfully",
                        "rule_id": rule_id
                    }
                }
            else:
                return {
                    "status": 404,
                    "data": {
                        "message": f"Rule {rule_id} not found"
                    }
                }
                
        except Exception as e:
            logger.error(f"Error in delete_rule: {str(e)}")
            return {
                "status": 500,
                "data": {
                    "message": f"Failed to delete rule: {str(e)}"
                }
            }
    
    def suggest_rules_for_client(self, client_name: str, data_context: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Suggest cleaning rules for a client based on their history and data context.
        
        Args:
            client_name: Name of the client
            data_context: Optional context about the data being processed
            
        Returns:
            List of suggested rule descriptions
        """
        try:
            suggestions = []
            
            # Get client's previous rules
            client_rules = self.client_rules.get(client_name, [])
            
            # Extract common patterns from previous rules
            if client_rules:
                suggestions.append("Apply previously used rules for this client")
                
                # Add specific suggestions based on rule history
                for rule in client_rules[-3:]:  # Last 3 rules
                    if rule["status"] == "active":
                        suggestions.append(f"Similar to: {rule['natural_language_rule'][:100]}...")
            
            # Add general suggestions
            suggestions.extend([
                "Flag lots where entry weight is below 500 pounds",
                "Remove lots with missing breed information",
                "Standardize date formats for birth dates",
                "Flag lots with unrealistic weight gain rates"
            ])
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error in suggest_rules_for_client: {str(e)}")
            return ["No suggestions available"]

