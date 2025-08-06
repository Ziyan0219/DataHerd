#!/usr/bin/env python3
"""
Test script for DataHerd LangGraph Workflow

This script tests the agentic workflow functionality independently
of the web API to ensure everything works correctly.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# Set environment variables
os.environ['PYTHONPATH'] = str(project_root)

def test_workflow_import():
    """Test if we can import the workflow module"""
    try:
        from dataherd.langgraph_workflow import create_dataherd_workflow, DataHerdWorkflow
        print("[OK] Successfully imported LangGraph workflow components")
        return True
    except ImportError as e:
        print(f"[ERROR] Failed to import workflow: {e}")
        return False

def test_workflow_creation():
    """Test workflow creation"""
    try:
        from dataherd.langgraph_workflow import create_dataherd_workflow
        workflow = create_dataherd_workflow()
        print("✅ Successfully created workflow instance")
        print(f"   Workflow type: {type(workflow).__name__}")
        return workflow
    except Exception as e:
        print(f"❌ Failed to create workflow: {e}")
        return None

def test_sample_data_processing():
    """Test workflow with sample data"""
    try:
        from dataherd.langgraph_workflow import create_dataherd_workflow
        
        # Sample cattle data
        test_data = {
            "records": [
                {"lot_id": "L001", "weight": 450, "breed": "angus", "birth_date": "2023-01-15"},
                {"lot_id": "L002", "weight": 320, "breed": "HEREFORD", "birth_date": "2023-02-20"}, 
                {"lot_id": "L003", "weight": 1800, "breed": "limousin", "birth_date": "2022-12-10"},
                {"lot_id": "L004", "weight": 600, "breed": "charolais", "birth_date": "2023-03-05"},
                {"lot_id": "L005", "weight": 250, "breed": "HOLSTEIN", "birth_date": "2023-04-10"}
            ],
            "total_count": 5,
            "columns": ["lot_id", "weight", "breed", "birth_date"]
        }
        
        print("[TEST] Testing workflow with sample cattle data...")
        
        workflow = create_dataherd_workflow()
        batch_id = "test_batch_001"
        
        print(f"   Processing batch: {batch_id}")
        print(f"   Records: {test_data['total_count']}")
        print(f"   Client context: Elanco Primary")
        
        # Run the workflow
        result = workflow.run_workflow(
            batch_id=batch_id,
            client_context="Elanco Primary", 
            initial_data=test_data
        )
        
        # Analyze results
        print("✅ Workflow execution completed!")
        print(f"   Batch ID: {result.get('batch_id')}")
        print(f"   Workflow Complete: {result.get('workflow_complete')}")
        print(f"   Current Step: {result.get('current_step')}")
        print(f"   Total Agent Messages: {len(result.get('messages', []))}")
        print(f"   Applied Changes: {len(result.get('applied_changes', []))}")
        
        # Quality metrics
        quality = result.get('quality_metrics', {})
        if quality:
            print(f"   Quality Score: {quality.get('overall_quality_score', 'N/A')}%")
            print(f"   Improvement: {quality.get('improvement_percentage', 'N/A')}%")
        
        # Operation log
        operations = result.get('operation_log', [])
        print(f"   Agent Operations: {len(operations)}")
        
        if operations:
            print("   Operation Timeline:")
            for op in operations:
                print(f"     - {op.get('agent', 'unknown')} -> {op.get('action', 'unknown')}")
        
        # Error check
        if result.get('error_message'):
            print(f"   ⚠️ Error: {result.get('error_message')}")
        
        # Applied changes details
        changes = result.get('applied_changes', [])
        if changes:
            print("   Sample Applied Changes:")
            for i, change in enumerate(changes[:3]):  # Show first 3
                print(f"     {i+1}. {change.get('record_id')} -> {change.get('field')}: {change.get('old_value')} -> {change.get('new_value')}")
        
        return result
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_individual_components():
    """Test individual DataHerd components"""
    print("[COMPONENTS] Testing individual components...")
    
    try:
        # Test NLP Processor
        from dataherd.nlp_processor import NLPProcessor
        nlp = NLPProcessor()
        print("✅ NLP Processor initialized")
        
        # Test Data Processor  
        from dataherd.data_processor import DataProcessor
        data_proc = DataProcessor()
        print("✅ Data Processor initialized")
        
        # Test Rule Manager
        from dataherd.rule_manager import RuleManager
        rule_mgr = RuleManager()
        print("✅ Rule Manager initialized")
        
        # Test Report Generator
        from dataherd.report_generator import ReportGenerator
        report_gen = ReportGenerator()
        print("✅ Report Generator initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        return False

def test_langgraph_dependencies():
    """Test LangGraph and LangChain dependencies"""
    print("[DEPS] Testing LangGraph dependencies...")
    
    dependencies = [
        ('langgraph', 'StateGraph'),
        ('langchain_core.messages', 'HumanMessage'),
        ('langchain_openai', 'ChatOpenAI'),
    ]
    
    success_count = 0
    for module, component in dependencies:
        try:
            exec(f"from {module} import {component}")
            print(f"✅ {module}.{component}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {module}.{component} - {e}")
    
    print(f"Dependencies: {success_count}/{len(dependencies)} available")
    return success_count == len(dependencies)

def main():
    """Run all tests"""
    print("=" * 60)
    print("DataHerd LangGraph Workflow Test Suite")
    print("=" * 60)
    
    tests = [
        ("Import Test", test_workflow_import),
        ("Dependencies Test", test_langgraph_dependencies),
        ("Component Test", test_individual_components),
        ("Workflow Creation Test", test_workflow_creation),
        ("Sample Data Processing Test", test_sample_data_processing),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n[TEST] Running {test_name}...")
        print("-" * 40)
        
        try:
            result = test_func()
            results[test_name] = "PASS" if result else "FAIL"
        except Exception as e:
            print(f"❌ Test crashed: {e}")
            results[test_name] = "CRASH"
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for r in results.values() if r == "PASS")
    total = len(results)
    
    for test_name, result in results.items():
        status = "PASS" if result == "PASS" else "FAIL" if result == "FAIL" else "CRASH"
        print(f"[{status}] {test_name}: {result}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("[SUCCESS] All tests passed! LangGraph workflow is ready for integration.")
    else:
        print("[WARNING] Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)