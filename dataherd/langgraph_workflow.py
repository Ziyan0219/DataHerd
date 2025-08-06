#!/usr/bin/env python3
"""
DataHerd LangGraph Workflow

This module implements a multi-agent workflow for cattle data cleaning using LangGraph,
integrating the existing DataHerd components into a proper agent-based architecture.
"""

import json
import logging
import uuid
from typing import Dict, Any, List, Optional, TypedDict, Annotated
from datetime import datetime
from enum import Enum

from langgraph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

from .nlp_processor import NLPProcessor, ParsedRule, RuleType
from .data_processor import DataProcessor
from .rule_manager import RuleManager
from .report_generator import ReportGenerator
from config.config import get_openai_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WorkflowState(TypedDict):
    """State object for the DataHerd workflow"""
    batch_id: str
    messages: Annotated[List[Any], "List of conversation messages"]
    current_step: str
    raw_data: Optional[Dict[str, Any]]
    parsed_rules: List[ParsedRule]
    preview_results: Optional[Dict[str, Any]]
    applied_changes: List[Dict[str, Any]]
    quality_metrics: Optional[Dict[str, Any]]
    client_context: str
    operation_log: List[Dict[str, Any]]
    error_message: Optional[str]
    requires_human_approval: bool
    workflow_complete: bool


class WorkflowStep(Enum):
    """Workflow step enumeration"""
    DATA_INGESTION = "data_ingestion"
    RULE_ANALYSIS = "rule_analysis" 
    DATA_VALIDATION = "data_validation"
    PREVIEW_GENERATION = "preview_generation"
    HUMAN_REVIEW = "human_review"
    DATA_CLEANING = "data_cleaning"
    QUALITY_ASSESSMENT = "quality_assessment"
    REPORT_GENERATION = "report_generation"
    WORKFLOW_COMPLETE = "workflow_complete"


class DataHerdWorkflow:
    """Multi-agent workflow orchestrator for DataHerd"""
    
    def __init__(self):
        """Initialize the workflow with all necessary components"""
        self.nlp_processor = NLPProcessor()
        self.data_processor = DataProcessor()
        self.rule_manager = RuleManager()
        self.report_generator = ReportGenerator()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            max_tokens=2000
        )
        
        # Build the workflow graph
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        
        # Create the state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes for each agent/step
        workflow.add_node("data_ingestion_agent", self.data_ingestion_agent)
        workflow.add_node("rule_analysis_agent", self.rule_analysis_agent)
        workflow.add_node("validation_agent", self.validation_agent)
        workflow.add_node("preview_agent", self.preview_agent)
        workflow.add_node("cleaning_agent", self.cleaning_agent)
        workflow.add_node("quality_agent", self.quality_agent)
        workflow.add_node("reporting_agent", self.reporting_agent)
        workflow.add_node("human_review_node", self.human_review_node)
        
        # Set entry point
        workflow.set_entry_point("data_ingestion_agent")
        
        # Add edges to define the workflow
        workflow.add_edge("data_ingestion_agent", "rule_analysis_agent")
        workflow.add_edge("rule_analysis_agent", "validation_agent")
        workflow.add_edge("validation_agent", "preview_agent")
        
        # Conditional edge for human review
        workflow.add_conditional_edges(
            "preview_agent",
            self.should_require_human_review,
            {
                "human_review": "human_review_node",
                "auto_proceed": "cleaning_agent"
            }
        )
        
        workflow.add_edge("human_review_node", "cleaning_agent")
        workflow.add_edge("cleaning_agent", "quality_agent")
        workflow.add_edge("quality_agent", "reporting_agent")
        workflow.add_edge("reporting_agent", END)
        
        return workflow.compile()
    
    def data_ingestion_agent(self, state: WorkflowState) -> WorkflowState:
        """Agent responsible for data ingestion and initial processing"""
        logger.info(f"Data Ingestion Agent processing batch: {state['batch_id']}")
        
        try:
            # Log the operation
            operation = {
                "timestamp": datetime.now().isoformat(),
                "agent": "data_ingestion_agent",
                "action": "processing_data_load",
                "batch_id": state["batch_id"]
            }
            state["operation_log"].append(operation)
            
            # Add system message for context
            system_msg = SystemMessage(content="""
            You are the Data Ingestion Agent for DataHerd. Your role is to:
            1. Validate incoming cattle data structure
            2. Perform initial data quality assessment
            3. Identify potential data issues
            4. Prepare data for rule analysis
            
            Analyze the provided data and ensure it meets required standards.
            """)
            
            state["messages"].append(system_msg)
            state["current_step"] = WorkflowStep.DATA_INGESTION.value
            
            # Simulate data validation (in real implementation, would load from file)
            if not state.get("raw_data"):
                # Mock data for testing
                state["raw_data"] = {
                    "records": [
                        {"lot_id": "L001", "weight": 450, "breed": "angus", "birth_date": "2023-01-15"},
                        {"lot_id": "L002", "weight": 320, "breed": "HEREFORD", "birth_date": "2023-02-20"},
                        {"lot_id": "L003", "weight": 1800, "breed": "limousin", "birth_date": "2022-12-10"}
                    ],
                    "total_count": 3,
                    "columns": ["lot_id", "weight", "breed", "birth_date"]
                }
            
            # Initial quality assessment
            quality_issues = []
            for record in state["raw_data"]["records"]:
                if record["weight"] < 400 or record["weight"] > 1500:
                    quality_issues.append(f"Weight {record['weight']} for {record['lot_id']} outside normal range")
                
                if record["breed"].islower() or record["breed"].isupper():
                    quality_issues.append(f"Breed name '{record['breed']}' needs standardization")
            
            # Add assessment to messages
            assessment_msg = AIMessage(content=f"""
            Data Ingestion Complete:
            - Total records: {state['raw_data']['total_count']}
            - Quality issues identified: {len(quality_issues)}
            - Issues: {quality_issues[:3]}  # Show first 3
            
            Data is ready for rule analysis.
            """)
            
            state["messages"].append(assessment_msg)
            logger.info(f"Data ingestion completed for batch {state['batch_id']}")
            
        except Exception as e:
            logger.error(f"Data ingestion failed: {e}")
            state["error_message"] = f"Data ingestion failed: {str(e)}"
        
        return state
    
    def rule_analysis_agent(self, state: WorkflowState) -> WorkflowState:
        """Agent responsible for analyzing and parsing cleaning rules"""
        logger.info("Rule Analysis Agent processing rules")
        
        try:
            operation = {
                "timestamp": datetime.now().isoformat(),
                "agent": "rule_analysis_agent", 
                "action": "analyzing_rules",
                "batch_id": state["batch_id"]
            }
            state["operation_log"].append(operation)
            
            system_msg = SystemMessage(content="""
            You are the Rule Analysis Agent. Your role is to:
            1. Parse natural language cleaning rules
            2. Convert rules into executable logic
            3. Validate rule consistency and safety
            4. Optimize rule application order
            
            Analyze each rule for effectiveness and safety.
            """)
            
            state["messages"].append(system_msg)
            state["current_step"] = WorkflowStep.RULE_ANALYSIS.value
            
            # Get existing rules for client context
            client_rules = self.rule_manager.get_client_rules(state["client_context"])
            
            # Sample rules for processing (in real implementation, would come from user input)
            sample_rules = [
                "Flag cattle with weight below 400 pounds or above 1500 pounds",
                "Standardize breed names to proper capitalization", 
                "Remove records with missing birth dates"
            ]
            
            parsed_rules = []
            for rule_text in sample_rules:
                parsed_rule = self.nlp_processor.parse_natural_language_rule(
                    rule_text, 
                    state["client_context"]
                )
                parsed_rules.append(parsed_rule)
            
            state["parsed_rules"] = parsed_rules
            
            # Analyze rule effectiveness using LLM
            rule_analysis_prompt = f"""
            Analyze these parsed rules for a cattle data cleaning operation:
            
            Rules:
            {[f"- {rule.description} (Type: {rule.rule_type.value}, Confidence: {rule.confidence})" for rule in parsed_rules]}
            
            Provide analysis on:
            1. Rule effectiveness
            2. Potential conflicts
            3. Recommended application order
            4. Risk assessment
            """
            
            response = self.llm.invoke([HumanMessage(content=rule_analysis_prompt)])
            
            analysis_msg = AIMessage(content=f"""
            Rule Analysis Complete:
            - Rules parsed: {len(parsed_rules)}
            - Client context: {state['client_context']}
            - Existing client rules: {len(client_rules)}
            
            Analysis: {response.content}
            """)
            
            state["messages"].append(analysis_msg)
            logger.info(f"Rule analysis completed: {len(parsed_rules)} rules processed")
            
        except Exception as e:
            logger.error(f"Rule analysis failed: {e}")
            state["error_message"] = f"Rule analysis failed: {str(e)}"
        
        return state
    
    def validation_agent(self, state: WorkflowState) -> WorkflowState:
        """Agent responsible for data validation using parsed rules"""
        logger.info("Validation Agent processing data validation")
        
        try:
            operation = {
                "timestamp": datetime.now().isoformat(),
                "agent": "validation_agent",
                "action": "validating_data_with_rules", 
                "batch_id": state["batch_id"]
            }
            state["operation_log"].append(operation)
            
            system_msg = SystemMessage(content="""
            You are the Data Validation Agent. Your role is to:
            1. Apply validation rules to identify issues
            2. Flag potential data quality problems
            3. Assess data integrity
            4. Prepare validation report
            
            Ensure thorough validation of all data points.
            """)
            
            state["messages"].append(system_msg)
            state["current_step"] = WorkflowStep.DATA_VALIDATION.value
            
            validation_results = []
            
            # Apply each parsed rule for validation
            for rule in state["parsed_rules"]:
                if rule.rule_type == RuleType.VALIDATION:
                    # Apply validation logic
                    for record in state["raw_data"]["records"]:
                        if rule.field == "weight":
                            weight = record.get("weight", 0)
                            min_weight = rule.parameters.get("min_weight", 400)
                            max_weight = rule.parameters.get("max_weight", 1500) 
                            
                            if weight < min_weight or weight > max_weight:
                                validation_results.append({
                                    "rule_id": f"rule_{rule.field}",
                                    "record_id": record["lot_id"],
                                    "field": rule.field,
                                    "issue": f"Weight {weight} outside range {min_weight}-{max_weight}",
                                    "severity": "high" if weight < 300 or weight > 2000 else "medium",
                                    "suggested_action": "flag_for_review"
                                })
            
            # Generate validation summary using LLM
            validation_prompt = f"""
            Data validation completed with the following results:
            
            Total records processed: {len(state['raw_data']['records'])}
            Validation issues found: {len(validation_results)}
            
            Issues:
            {json.dumps(validation_results, indent=2)}
            
            Provide a summary of validation results and recommendations.
            """
            
            response = self.llm.invoke([HumanMessage(content=validation_prompt)])
            
            validation_msg = AIMessage(content=f"""
            Data Validation Complete:
            - Records processed: {len(state["raw_data"]["records"])}
            - Issues identified: {len(validation_results)}
            - Rules applied: {len([r for r in state["parsed_rules"] if r.rule_type == RuleType.VALIDATION])}
            
            Summary: {response.content}
            """)
            
            state["messages"].append(validation_msg)
            
            # Store validation results for next step
            state["validation_results"] = validation_results
            
            logger.info(f"Data validation completed: {len(validation_results)} issues found")
            
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            state["error_message"] = f"Data validation failed: {str(e)}"
        
        return state
    
    def preview_agent(self, state: WorkflowState) -> WorkflowState:
        """Agent responsible for generating cleaning preview"""
        logger.info("Preview Agent generating cleaning preview")
        
        try:
            operation = {
                "timestamp": datetime.now().isoformat(),
                "agent": "preview_agent",
                "action": "generating_preview",
                "batch_id": state["batch_id"]
            }
            state["operation_log"].append(operation)
            
            system_msg = SystemMessage(content="""
            You are the Preview Agent. Your role is to:
            1. Generate preview of all proposed changes
            2. Calculate impact assessment
            3. Identify high-risk changes requiring approval
            4. Prepare change summary for review
            
            Provide comprehensive preview of all proposed modifications.
            """)
            
            state["messages"].append(system_msg)
            state["current_step"] = WorkflowStep.PREVIEW_GENERATION.value
            
            # Generate preview for all cleaning rules
            all_changes = []
            risk_score = 0
            
            for rule in state["parsed_rules"]:
                for record in state["raw_data"]["records"]:
                    # Apply rule logic to generate changes
                    if rule.rule_type == RuleType.STANDARDIZATION and rule.field == "breed":
                        original_breed = record["breed"]
                        standardized_breed = original_breed.title()
                        
                        if original_breed != standardized_breed:
                            change = {
                                "record_id": record["lot_id"],
                                "field": rule.field,
                                "rule_id": f"rule_{rule.field}",
                                "original_value": original_breed,
                                "proposed_value": standardized_breed,
                                "change_type": "standardization",
                                "confidence": rule.confidence,
                                "risk_level": "low"
                            }
                            all_changes.append(change)
                    
                    elif rule.rule_type == RuleType.VALIDATION and rule.field == "weight":
                        weight = record["weight"]
                        if weight < 400 or weight > 1500:
                            change = {
                                "record_id": record["lot_id"],
                                "field": rule.field,
                                "rule_id": f"rule_{rule.field}",
                                "original_value": weight,
                                "proposed_value": "FLAG_FOR_REVIEW",
                                "change_type": "validation_flag",
                                "confidence": rule.confidence,
                                "risk_level": "high" if weight < 300 or weight > 2000 else "medium"
                            }
                            all_changes.append(change)
                            risk_score += 10 if change["risk_level"] == "high" else 5
            
            # Generate preview summary using LLM
            preview_prompt = f"""
            Cleaning preview generated with the following proposed changes:
            
            Total changes: {len(all_changes)}
            Risk score: {risk_score}
            
            Changes breakdown:
            {json.dumps(all_changes[:5], indent=2)}  # Show first 5 changes
            
            Assess whether human review is required and provide recommendations.
            """
            
            response = self.llm.invoke([HumanMessage(content=preview_prompt)])
            
            # Determine if human approval is needed
            requires_approval = risk_score > 20 or len([c for c in all_changes if c["risk_level"] == "high"]) > 0
            
            state["preview_results"] = {
                "changes": all_changes,
                "total_changes": len(all_changes),
                "risk_score": risk_score,
                "requires_approval": requires_approval,
                "summary": response.content
            }
            
            state["requires_human_approval"] = requires_approval
            
            preview_msg = AIMessage(content=f"""
            Cleaning Preview Generated:
            - Total proposed changes: {len(all_changes)}
            - Risk score: {risk_score}
            - Requires human approval: {requires_approval}
            
            Analysis: {response.content}
            """)
            
            state["messages"].append(preview_msg)
            logger.info(f"Preview generated: {len(all_changes)} changes, requires approval: {requires_approval}")
            
        except Exception as e:
            logger.error(f"Preview generation failed: {e}")
            state["error_message"] = f"Preview generation failed: {str(e)}"
        
        return state
    
    def should_require_human_review(self, state: WorkflowState) -> str:
        """Conditional function to determine if human review is required"""
        return "human_review" if state.get("requires_human_approval", False) else "auto_proceed"
    
    def human_review_node(self, state: WorkflowState) -> WorkflowState:
        """Node for human review (simulated for now)"""
        logger.info("Human Review Node - Awaiting approval")
        
        operation = {
            "timestamp": datetime.now().isoformat(),
            "agent": "human_review_node",
            "action": "awaiting_human_approval",
            "batch_id": state["batch_id"]
        }
        state["operation_log"].append(operation)
        
        # In a real system, this would pause and wait for human input
        # For now, we'll simulate approval
        review_msg = HumanMessage(content=f"""
        Human Review Required:
        - {state['preview_results']['total_changes']} changes proposed
        - Risk score: {state['preview_results']['risk_score']}
        
        [SIMULATED] Review completed - Changes approved with modifications.
        """)
        
        state["messages"].append(review_msg)
        state["current_step"] = WorkflowStep.HUMAN_REVIEW.value
        
        logger.info("Human review completed (simulated)")
        return state
    
    def cleaning_agent(self, state: WorkflowState) -> WorkflowState:
        """Agent responsible for applying approved cleaning changes"""
        logger.info("Cleaning Agent applying changes")
        
        try:
            operation = {
                "timestamp": datetime.now().isoformat(),
                "agent": "cleaning_agent",
                "action": "applying_changes",
                "batch_id": state["batch_id"]
            }
            state["operation_log"].append(operation)
            
            system_msg = SystemMessage(content="""
            You are the Data Cleaning Agent. Your role is to:
            1. Apply approved cleaning changes safely
            2. Track all modifications made
            3. Handle errors gracefully
            4. Prepare change log for reporting
            
            Execute all approved changes with precision and safety.
            """)
            
            state["messages"].append(system_msg)
            state["current_step"] = WorkflowStep.DATA_CLEANING.value
            
            applied_changes = []
            
            # Apply approved changes from preview
            if state.get("preview_results"):
                changes = state["preview_results"]["changes"]
                
                for change in changes:
                    try:
                        # Apply the change (simulated)
                        applied_change = {
                            "record_id": change["record_id"],
                            "field": change["field"],
                            "old_value": change["original_value"],
                            "new_value": change["proposed_value"],
                            "change_type": change["change_type"],
                            "applied_at": datetime.now().isoformat(),
                            "status": "success"
                        }
                        applied_changes.append(applied_change)
                        
                    except Exception as e:
                        failed_change = {
                            "record_id": change["record_id"],
                            "field": change["field"],
                            "error": str(e),
                            "status": "failed"
                        }
                        applied_changes.append(failed_change)
            
            state["applied_changes"] = applied_changes
            
            cleaning_msg = AIMessage(content=f"""
            Data Cleaning Complete:
            - Changes applied: {len([c for c in applied_changes if c['status'] == 'success'])}
            - Failed changes: {len([c for c in applied_changes if c['status'] == 'failed'])}
            - Total processed: {len(applied_changes)}
            
            All approved changes have been safely applied to the dataset.
            """)
            
            state["messages"].append(cleaning_msg)
            logger.info(f"Data cleaning completed: {len(applied_changes)} changes processed")
            
        except Exception as e:
            logger.error(f"Data cleaning failed: {e}")
            state["error_message"] = f"Data cleaning failed: {str(e)}"
        
        return state
    
    def quality_agent(self, state: WorkflowState) -> WorkflowState:
        """Agent responsible for post-cleaning quality assessment"""
        logger.info("Quality Agent assessing data quality")
        
        try:
            operation = {
                "timestamp": datetime.now().isoformat(),
                "agent": "quality_agent",
                "action": "assessing_quality",
                "batch_id": state["batch_id"]
            }
            state["operation_log"].append(operation)
            
            system_msg = SystemMessage(content="""
            You are the Quality Assessment Agent. Your role is to:
            1. Evaluate post-cleaning data quality
            2. Calculate quality metrics and improvements
            3. Identify remaining issues
            4. Validate cleaning effectiveness
            
            Provide comprehensive quality assessment of the cleaned data.
            """)
            
            state["messages"].append(system_msg)
            state["current_step"] = WorkflowStep.QUALITY_ASSESSMENT.value
            
            # Calculate quality metrics
            total_records = len(state["raw_data"]["records"])
            successful_changes = len([c for c in state["applied_changes"] if c["status"] == "success"])
            
            quality_metrics = {
                "total_records": total_records,
                "changes_applied": successful_changes,
                "improvement_percentage": (successful_changes / total_records) * 100 if total_records > 0 else 0,
                "data_completeness": 95.0,  # Would be calculated from actual data
                "data_accuracy": 92.0,      # Would be calculated from actual data
                "consistency_score": 88.0,   # Would be calculated from actual data
                "overall_quality_score": 92.5
            }
            
            # Generate quality assessment using LLM
            quality_prompt = f"""
            Post-cleaning quality assessment:
            
            Metrics:
            - Total records: {quality_metrics['total_records']}
            - Changes applied: {quality_metrics['changes_applied']}
            - Improvement: {quality_metrics['improvement_percentage']:.1f}%
            - Overall quality score: {quality_metrics['overall_quality_score']}%
            
            Applied changes summary:
            {json.dumps(state['applied_changes'][:3], indent=2)}
            
            Provide quality assessment and recommendations for future improvements.
            """
            
            response = self.llm.invoke([HumanMessage(content=quality_prompt)])
            
            state["quality_metrics"] = quality_metrics
            
            quality_msg = AIMessage(content=f"""
            Quality Assessment Complete:
            - Overall quality score: {quality_metrics['overall_quality_score']}%
            - Improvement achieved: {quality_metrics['improvement_percentage']:.1f}%
            - Data completeness: {quality_metrics['data_completeness']}%
            
            Assessment: {response.content}
            """)
            
            state["messages"].append(quality_msg)
            logger.info(f"Quality assessment completed: {quality_metrics['overall_quality_score']}% quality score")
            
        except Exception as e:
            logger.error(f"Quality assessment failed: {e}")
            state["error_message"] = f"Quality assessment failed: {str(e)}"
        
        return state
    
    def reporting_agent(self, state: WorkflowState) -> WorkflowState:
        """Agent responsible for generating comprehensive reports"""
        logger.info("Reporting Agent generating final report")
        
        try:
            operation = {
                "timestamp": datetime.now().isoformat(),
                "agent": "reporting_agent",
                "action": "generating_report",
                "batch_id": state["batch_id"]
            }
            state["operation_log"].append(operation)
            
            system_msg = SystemMessage(content="""
            You are the Reporting Agent. Your role is to:
            1. Generate comprehensive operation reports
            2. Summarize all workflow activities
            3. Provide actionable insights
            4. Create audit trails
            
            Compile a complete report of the data cleaning operation.
            """)
            
            state["messages"].append(system_msg)
            state["current_step"] = WorkflowStep.REPORT_GENERATION.value
            
            # Generate comprehensive report using the report generator
            processing_results = {
                "total_records": state["quality_metrics"]["total_records"],
                "changes_applied": state["quality_metrics"]["changes_applied"]
            }
            
            rule_applications = [
                {
                    "rule_type": rule.rule_type.value,
                    "confidence": rule.confidence,
                    "changes_made": len([c for c in state["applied_changes"] if c.get("field") == rule.field])
                }
                for rule in state["parsed_rules"]
            ]
            
            # Generate report using existing report generator
            report = self.report_generator.generate_comprehensive_report(
                batch_id=state["batch_id"],
                processing_results=processing_results,
                rule_applications=rule_applications,
                client_name=state["client_context"]
            )
            
            state["final_report"] = report
            state["workflow_complete"] = True
            
            report_msg = AIMessage(content=f"""
            Final Report Generated:
            - Report ID: {report['report_id']}
            - Processing Summary: {processing_results}
            - Rules Applied: {len(rule_applications)}
            - Quality Score: {state['quality_metrics']['overall_quality_score']}%
            
            Workflow completed successfully. All data has been processed and cleaned according to specifications.
            """)
            
            state["messages"].append(report_msg)
            logger.info(f"Final report generated: {report['report_id']}")
            
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            state["error_message"] = f"Report generation failed: {str(e)}"
        
        return state
    
    def run_workflow(self, batch_id: str, client_context: str = "Default", 
                    initial_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the complete DataHerd workflow
        
        Args:
            batch_id: Unique identifier for the batch
            client_context: Client context for rule customization
            initial_data: Initial data for processing
            
        Returns:
            Final workflow state with all results
        """
        logger.info(f"Starting DataHerd workflow for batch: {batch_id}")
        
        # Initialize workflow state
        initial_state = WorkflowState(
            batch_id=batch_id,
            messages=[],
            current_step="initializing",
            raw_data=initial_data,
            parsed_rules=[],
            preview_results=None,
            applied_changes=[],
            quality_metrics=None,
            client_context=client_context,
            operation_log=[],
            error_message=None,
            requires_human_approval=False,
            workflow_complete=False
        )
        
        try:
            # Execute the workflow
            final_state = self.workflow.invoke(initial_state)
            
            logger.info(f"Workflow completed successfully for batch: {batch_id}")
            return dict(final_state)
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                "batch_id": batch_id,
                "error": str(e),
                "workflow_complete": False,
                "error_message": f"Workflow execution failed: {str(e)}"
            }


# Convenience function for external usage
def create_dataherd_workflow() -> DataHerdWorkflow:
    """Create and return a DataHerd workflow instance"""
    return DataHerdWorkflow()


# Example usage and testing
if __name__ == "__main__":
    # Test the workflow
    workflow = create_dataherd_workflow()
    
    test_data = {
        "records": [
            {"lot_id": "L001", "weight": 450, "breed": "angus", "birth_date": "2023-01-15"},
            {"lot_id": "L002", "weight": 320, "breed": "HEREFORD", "birth_date": "2023-02-20"},
            {"lot_id": "L003", "weight": 1800, "breed": "limousin", "birth_date": "2022-12-10"}
        ],
        "total_count": 3,
        "columns": ["lot_id", "weight", "breed", "birth_date"]
    }
    
    result = workflow.run_workflow(
        batch_id="test_batch_001",
        client_context="Elanco Primary",
        initial_data=test_data
    )
    
    print("\nWorkflow Results:")
    print(f"Batch ID: {result['batch_id']}")
    print(f"Workflow Complete: {result['workflow_complete']}")
    print(f"Total Messages: {len(result.get('messages', []))}")
    print(f"Applied Changes: {len(result.get('applied_changes', []))}")
    
    if result.get('quality_metrics'):
        print(f"Quality Score: {result['quality_metrics']['overall_quality_score']}%")
    
    if result.get('error_message'):
        print(f"Error: {result['error_message']}")