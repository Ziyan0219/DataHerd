"""
Rule Manager for DataHerd
Handles rule persistence, management, and application with client-specific contexts
"""

import json
import sqlite3
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
import uuid
from .nlp_processor import ParsedRule, RuleType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SavedRule:
    """Represents a saved rule with metadata"""
    id: str
    name: str
    description: str
    rule_type: str
    field: str
    condition: str
    action: str
    parameters: Dict[str, Any]
    confidence: float
    client_context: str
    is_permanent: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    usage_count: int
    success_rate: float
    last_used: Optional[datetime] = None

class RuleManager:
    """Manages data cleaning rules with persistence and client-specific contexts"""
    
    def __init__(self, db_path: str = "dataherd_rules.db"):
        self.db_path = db_path
        self.init_database()
        self.rule_cache = {}
        
    def init_database(self):
        """Initialize the rules database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create rules table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rules (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    rule_type TEXT NOT NULL,
                    field TEXT NOT NULL,
                    condition TEXT,
                    action TEXT NOT NULL,
                    parameters TEXT,
                    confidence REAL,
                    client_context TEXT,
                    is_permanent BOOLEAN DEFAULT FALSE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    usage_count INTEGER DEFAULT 0,
                    success_rate REAL DEFAULT 0.0,
                    last_used TIMESTAMP
                )
            ''')
            
            # Create rule applications table for tracking usage
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rule_applications (
                    id TEXT PRIMARY KEY,
                    rule_id TEXT,
                    batch_id TEXT,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN,
                    changes_made INTEGER,
                    confidence_achieved REAL,
                    FOREIGN KEY (rule_id) REFERENCES rules (id)
                )
            ''')
            
            # Create client-specific rule templates
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS client_templates (
                    id TEXT PRIMARY KEY,
                    client_name TEXT NOT NULL,
                    template_name TEXT NOT NULL,
                    template_rules TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE
                )
            ''')
            
            conn.commit()
            conn.close()
            
            logger.info("Rules database initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            raise
    
    def save_rule(self, parsed_rule: ParsedRule, name: str, client_context: str = "", 
                  is_permanent: bool = False) -> str:
        """
        Save a parsed rule to the database
        
        Args:
            parsed_rule: ParsedRule object to save
            name: Human-readable name for the rule
            client_context: Client-specific context
            is_permanent: Whether this rule should be permanently saved
            
        Returns:
            Rule ID
        """
        try:
            rule_id = str(uuid.uuid4())
            
            saved_rule = SavedRule(
                id=rule_id,
                name=name,
                description=parsed_rule.description,
                rule_type=parsed_rule.rule_type.value,
                field=parsed_rule.field,
                condition=parsed_rule.condition,
                action=parsed_rule.action,
                parameters=parsed_rule.parameters,
                confidence=parsed_rule.confidence,
                client_context=client_context,
                is_permanent=is_permanent,
                is_active=True,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                usage_count=0,
                success_rate=0.0
            )
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO rules (
                    id, name, description, rule_type, field, condition, action,
                    parameters, confidence, client_context, is_permanent, is_active,
                    created_at, updated_at, usage_count, success_rate
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                saved_rule.id, saved_rule.name, saved_rule.description,
                saved_rule.rule_type, saved_rule.field, saved_rule.condition,
                saved_rule.action, json.dumps(saved_rule.parameters),
                saved_rule.confidence, saved_rule.client_context,
                saved_rule.is_permanent, saved_rule.is_active,
                saved_rule.created_at, saved_rule.updated_at,
                saved_rule.usage_count, saved_rule.success_rate
            ))
            
            conn.commit()
            conn.close()
            
            # Cache the rule
            self.rule_cache[rule_id] = saved_rule
            
            logger.info(f"Rule '{name}' saved with ID: {rule_id}")
            return rule_id
            
        except Exception as e:
            logger.error(f"Error saving rule: {str(e)}")
            raise
    
    def load_rule(self, rule_id: str) -> Optional[SavedRule]:
        """Load a rule by ID"""
        try:
            # Check cache first
            if rule_id in self.rule_cache:
                return self.rule_cache[rule_id]
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT * FROM rules WHERE id = ?', (rule_id,))
            row = cursor.fetchone()
            conn.close()
            
            if row:
                saved_rule = self._row_to_saved_rule(row)
                self.rule_cache[rule_id] = saved_rule
                return saved_rule
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading rule {rule_id}: {str(e)}")
            return None
    
    def get_rules_by_client(self, client_context: str, active_only: bool = True) -> List[SavedRule]:
        """Get all rules for a specific client"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = 'SELECT * FROM rules WHERE client_context = ?'
            params = [client_context]
            
            if active_only:
                query += ' AND is_active = ?'
                params.append(True)
            
            query += ' ORDER BY created_at DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_saved_rule(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting rules for client {client_context}: {str(e)}")
            return []
    
    def get_all_rules(self, active_only: bool = True) -> List[SavedRule]:
        """Get all rules"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = 'SELECT * FROM rules'
            params = []
            
            if active_only:
                query += ' WHERE is_active = ?'
                params.append(True)
            
            query += ' ORDER BY created_at DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            
            return [self._row_to_saved_rule(row) for row in rows]
            
        except Exception as e:
            logger.error(f"Error getting all rules: {str(e)}")
            return []
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """Update a rule"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build update query dynamically
            set_clauses = []
            params = []
            
            for key, value in updates.items():
                if key in ['name', 'description', 'condition', 'action', 'client_context']:
                    set_clauses.append(f'{key} = ?')
                    params.append(value)
                elif key == 'parameters':
                    set_clauses.append('parameters = ?')
                    params.append(json.dumps(value))
                elif key in ['confidence', 'success_rate']:
                    set_clauses.append(f'{key} = ?')
                    params.append(float(value))
                elif key in ['is_permanent', 'is_active']:
                    set_clauses.append(f'{key} = ?')
                    params.append(bool(value))
                elif key == 'usage_count':
                    set_clauses.append('usage_count = ?')
                    params.append(int(value))
            
            if not set_clauses:
                return False
            
            set_clauses.append('updated_at = ?')
            params.append(datetime.now())
            params.append(rule_id)
            
            query = f"UPDATE rules SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, params)
            
            conn.commit()
            conn.close()
            
            # Clear cache for this rule
            if rule_id in self.rule_cache:
                del self.rule_cache[rule_id]
            
            logger.info(f"Rule {rule_id} updated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error updating rule {rule_id}: {str(e)}")
            return False
    
    def delete_rule(self, rule_id: str) -> bool:
        """Delete a rule (soft delete by setting is_active to False)"""
        return self.update_rule(rule_id, {'is_active': False})
    
    def record_rule_application(self, rule_id: str, batch_id: str, success: bool, 
                              changes_made: int, confidence_achieved: float):
        """Record the application of a rule for tracking purposes"""
        try:
            application_id = str(uuid.uuid4())
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Insert application record
            cursor.execute('''
                INSERT INTO rule_applications (
                    id, rule_id, batch_id, applied_at, success, changes_made, confidence_achieved
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                application_id, rule_id, batch_id, datetime.now(),
                success, changes_made, confidence_achieved
            ))
            
            # Update rule usage statistics
            cursor.execute('''
                UPDATE rules SET 
                    usage_count = usage_count + 1,
                    last_used = ?,
                    success_rate = (
                        SELECT AVG(CASE WHEN success THEN 1.0 ELSE 0.0 END) 
                        FROM rule_applications 
                        WHERE rule_id = ?
                    )
                WHERE id = ?
            ''', (datetime.now(), rule_id, rule_id))
            
            conn.commit()
            conn.close()
            
            # Clear cache for this rule
            if rule_id in self.rule_cache:
                del self.rule_cache[rule_id]
            
            logger.info(f"Rule application recorded for rule {rule_id}")
            
        except Exception as e:
            logger.error(f"Error recording rule application: {str(e)}")
    
    def get_rule_statistics(self, rule_id: str) -> Dict[str, Any]:
        """Get usage statistics for a rule"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get basic rule info
            cursor.execute('SELECT * FROM rules WHERE id = ?', (rule_id,))
            rule_row = cursor.fetchone()
            
            if not rule_row:
                return {}
            
            # Get application statistics
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_applications,
                    SUM(CASE WHEN success THEN 1 ELSE 0 END) as successful_applications,
                    AVG(changes_made) as avg_changes_made,
                    AVG(confidence_achieved) as avg_confidence_achieved,
                    MAX(applied_at) as last_applied
                FROM rule_applications 
                WHERE rule_id = ?
            ''', (rule_id,))
            
            stats_row = cursor.fetchone()
            conn.close()
            
            rule = self._row_to_saved_rule(rule_row)
            
            return {
                'rule_id': rule_id,
                'rule_name': rule.name,
                'rule_type': rule.rule_type,
                'field': rule.field,
                'client_context': rule.client_context,
                'is_permanent': rule.is_permanent,
                'created_at': rule.created_at,
                'usage_count': rule.usage_count,
                'success_rate': rule.success_rate,
                'last_used': rule.last_used,
                'total_applications': stats_row[0] if stats_row else 0,
                'successful_applications': stats_row[1] if stats_row else 0,
                'avg_changes_made': stats_row[2] if stats_row else 0,
                'avg_confidence_achieved': stats_row[3] if stats_row else 0,
                'last_applied': stats_row[4] if stats_row else None
            }
            
        except Exception as e:
            logger.error(f"Error getting rule statistics: {str(e)}")
            return {}
    
    def create_client_template(self, client_name: str, template_name: str, 
                             rule_ids: List[str]) -> str:
        """Create a template of rules for a specific client"""
        try:
            template_id = str(uuid.uuid4())
            
            # Get the rules
            rules_data = []
            for rule_id in rule_ids:
                rule = self.load_rule(rule_id)
                if rule:
                    rules_data.append(asdict(rule))
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO client_templates (
                    id, client_name, template_name, template_rules, created_at, is_active
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                template_id, client_name, template_name,
                json.dumps(rules_data), datetime.now(), True
            ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Client template '{template_name}' created for {client_name}")
            return template_id
            
        except Exception as e:
            logger.error(f"Error creating client template: {str(e)}")
            raise
    
    def apply_client_template(self, client_name: str, template_name: str) -> List[str]:
        """Apply a client template to create new rule instances"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT template_rules FROM client_templates 
                WHERE client_name = ? AND template_name = ? AND is_active = ?
            ''', (client_name, template_name, True))
            
            row = cursor.fetchone()
            conn.close()
            
            if not row:
                raise ValueError(f"Template '{template_name}' not found for client '{client_name}'")
            
            template_rules = json.loads(row[0])
            new_rule_ids = []
            
            # Create new rule instances from template
            for rule_data in template_rules:
                # Convert back to ParsedRule
                parsed_rule = ParsedRule(
                    rule_type=RuleType(rule_data['rule_type']),
                    field=rule_data['field'],
                    condition=rule_data['condition'],
                    action=rule_data['action'],
                    parameters=rule_data['parameters'],
                    confidence=rule_data['confidence'],
                    description=rule_data['description']
                )
                
                # Save as new rule
                rule_id = self.save_rule(
                    parsed_rule=parsed_rule,
                    name=f"{rule_data['name']} (from template)",
                    client_context=client_name,
                    is_permanent=rule_data['is_permanent']
                )
                new_rule_ids.append(rule_id)
            
            logger.info(f"Applied template '{template_name}' for {client_name}, created {len(new_rule_ids)} rules")
            return new_rule_ids
            
        except Exception as e:
            logger.error(f"Error applying client template: {str(e)}")
            raise
    
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
            client_rules = self.get_rules_by_client(client_name)
            
            # Extract common patterns from previous rules
            if client_rules:
                suggestions.append("Apply previously used rules for this client")
                
                # Add specific suggestions based on rule history
                for rule in client_rules[-3:]:  # Last 3 rules
                    if rule.is_active:
                        suggestions.append(f"Similar to: {rule.description[:100]}...")
            
            # Add general suggestions based on cattle data best practices
            suggestions.extend([
                "Flag weights below 400 lbs or above 1500 lbs as potential errors",
                "Standardize breed names to proper capitalization",
                "Validate birth dates are within reasonable range (not future dates)",
                "Remove duplicate entries based on lot ID",
                "Flag missing or null values in critical fields"
            ])
            
            return suggestions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error in suggest_rules_for_client: {str(e)}")
            return ["No suggestions available"]
    
    def _row_to_saved_rule(self, row) -> SavedRule:
        """Convert database row to SavedRule object"""
        return SavedRule(
            id=row[0],
            name=row[1],
            description=row[2],
            rule_type=row[3],
            field=row[4],
            condition=row[5],
            action=row[6],
            parameters=json.loads(row[7]) if row[7] else {},
            confidence=row[8],
            client_context=row[9],
            is_permanent=bool(row[10]),
            is_active=bool(row[11]),
            created_at=datetime.fromisoformat(row[12]) if row[12] else datetime.now(),
            updated_at=datetime.fromisoformat(row[13]) if row[13] else datetime.now(),
            usage_count=row[14],
            success_rate=row[15],
            last_used=datetime.fromisoformat(row[16]) if row[16] else None
        )
    
    def export_rules(self, client_context: str = None, file_path: str = None) -> str:
        """Export rules to JSON file"""
        try:
            if client_context:
                rules = self.get_rules_by_client(client_context, active_only=False)
            else:
                rules = self.get_all_rules(active_only=False)
            
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'client_context': client_context,
                'rules_count': len(rules),
                'rules': [asdict(rule) for rule in rules]
            }
            
            if not file_path:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                client_suffix = f"_{client_context}" if client_context else ""
                file_path = f"dataherd_rules_export{client_suffix}_{timestamp}.json"
            
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
            
            logger.info(f"Exported {len(rules)} rules to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error exporting rules: {str(e)}")
            raise
    
    def import_rules(self, file_path: str, client_context: str = None) -> List[str]:
        """Import rules from JSON file"""
        try:
            with open(file_path, 'r') as f:
                import_data = json.load(f)
            
            rules_data = import_data.get('rules', [])
            imported_rule_ids = []
            
            for rule_data in rules_data:
                # Convert to ParsedRule
                parsed_rule = ParsedRule(
                    rule_type=RuleType(rule_data['rule_type']),
                    field=rule_data['field'],
                    condition=rule_data['condition'],
                    action=rule_data['action'],
                    parameters=rule_data['parameters'],
                    confidence=rule_data['confidence'],
                    description=rule_data['description']
                )
                
                # Use provided client_context or original
                context = client_context or rule_data.get('client_context', '')
                
                # Save rule
                rule_id = self.save_rule(
                    parsed_rule=parsed_rule,
                    name=rule_data['name'],
                    client_context=context,
                    is_permanent=rule_data.get('is_permanent', False)
                )
                imported_rule_ids.append(rule_id)
            
            logger.info(f"Imported {len(imported_rule_ids)} rules from {file_path}")
            return imported_rule_ids
            
        except Exception as e:
            logger.error(f"Error importing rules: {str(e)}")
            raise

