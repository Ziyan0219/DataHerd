#!/usr/bin/env python3
"""
DataHerd Core Functionality Test Script
Tests all major components to ensure they work correctly
"""

import sys
import json
import pandas as pd
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_nlp_processor():
    """Test NLP Processor functionality"""
    print("🧠 Testing NLP Processor...")
    
    try:
        from dataherd.nlp_processor import NLPProcessor
        
        nlp = NLPProcessor()
        
        # Test rule parsing
        test_rule = "Flag any cattle with weight below 400 pounds for Elanco"
        parsed_rule = nlp.parse_natural_language_rule(test_rule, "Elanco")
        
        print(f"   ✓ Rule parsed: {parsed_rule.rule_type}")
        print(f"   ✓ Field: {parsed_rule.field}")
        print(f"   ✓ Confidence: {parsed_rule.confidence:.2f}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ NLP Processor test failed: {str(e)}")
        return False

def test_rule_manager():
    """Test Rule Manager functionality"""
    print("📋 Testing Rule Manager...")
    
    try:
        from dataherd.rule_manager import RuleManager
        from dataherd.nlp_processor import ParsedRule, RuleType
        
        rule_mgr = RuleManager()
        
        # Test rule saving with ParsedRule object
        test_parsed_rule = ParsedRule(
            rule_type=RuleType.VALIDATION,
            field='weight',
            condition='weight < 400',
            action='flag_as_error',
            parameters={'min_weight': 400},
            confidence=0.95,
            description='Test rule for weight validation'
        )
        
        rule_id = rule_mgr.save_rule(
            test_parsed_rule, 
            'Test Weight Validation',
            'Test Client'
        )
        print(f"   ✓ Rule saved with ID: {rule_id}")
        
        # Test rule retrieval
        saved_rule = rule_mgr.get_rule(rule_id)
        print(f"   ✓ Rule retrieved: {saved_rule['name']}")
        
        # Test client rules
        client_rules = rule_mgr.get_client_rules('Test Client')
        print(f"   ✓ Client rules found: {len(client_rules)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Rule Manager test failed: {str(e)}")
        return False

def test_data_processor():
    """Test Data Processor functionality"""
    print("🔄 Testing Data Processor...")
    
    try:
        from dataherd.data_processor import DataProcessor
        import tempfile
        import os
        
        data_proc = DataProcessor()
        
        # Create test data
        test_data = pd.DataFrame({
            'lot_id': ['LOT001', 'LOT002', 'LOT003'],
            'weight': [350, 800, 1600],  # One below, one normal, one above threshold
            'breed': ['angus', 'Hereford', 'CHAROLAIS'],
            'birth_date': ['2023-01-15', '2023-02-20', '2023-03-10'],
            'health_status': ['healthy', 'healthy', 'sick']
        })
        
        # Save test data to temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            test_data.to_csv(f.name, index=False)
            temp_file = f.name
        
        try:
            # Test data loading
            loaded_data = data_proc.load_data(temp_file, 'test_batch_001')
            print(f"   ✓ Data loaded: {len(loaded_data)} records")
            
            # Test preview functionality with sample data
            preview_results = data_proc.preview_cleaning_operation(
                'test_batch_001',
                "Flag cattle with weight below 400 pounds or above 1500 pounds",
                'Test Client'
            )
            print(f"   ✓ Preview generated successfully")
            
        finally:
            # Cleanup temporary file
            os.unlink(temp_file)
        
        return True
        
    except Exception as e:
        print(f"   ❌ Data Processor test failed: {str(e)}")
        return False

def test_report_generator():
    """Test Report Generator functionality"""
    print("📊 Testing Report Generator...")
    
    try:
        from dataherd.report_generator import ReportGenerator
        
        report_gen = ReportGenerator()
        
        # Create mock processing results
        mock_results = {
            'original_count': 100,
            'changes_applied': [
                {'rule_type': 'validation', 'field': 'weight', 'original': '350', 'suggested': 'FLAGGED'},
                {'rule_type': 'standardization', 'field': 'breed', 'original': 'angus', 'suggested': 'Angus'}
            ],
            'issues_found': [
                {'rule_type': 'validation', 'field': 'weight', 'issue': 'Below minimum weight'}
            ],
            'summary': {
                'data_quality_improvement': 15.2
            }
        }
        
        mock_rule_applications = [
            {'rule_type': 'validation', 'confidence': 0.95},
            {'rule_type': 'standardization', 'confidence': 0.98}
        ]
        
        # Test comprehensive report generation
        report = report_gen.generate_comprehensive_report(
            'test_batch_001',
            mock_results,
            mock_rule_applications,
            'Test Client'
        )
        
        print(f"   ✓ Report generated with ID: {report['report_id']}")
        print(f"   ✓ Report sections: {len(report['sections'])}")
        print(f"   ✓ Report metadata: {len(report['metadata'])} items")
        
        # Test operation report
        operation_report = report_gen.generate_operation_report()
        print(f"   ✓ Operation report generated: {operation_report['report_id']}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Report Generator test failed: {str(e)}")
        return False

def test_database_models():
    """Test Database Models"""
    print("🗄️  Testing Database Models...")
    
    try:
        from db.models import CattleRecord
        from db.base import SessionLocal
        
        # Test database connection
        session = SessionLocal()
        
        # Test model creation
        test_record = CattleRecord(
            lot_id='TEST001',
            weight=750.5,
            breed='Angus',
            birth_date=datetime(2023, 1, 15),
            health_status='healthy',
            feed_type='grain'
        )
        
        session.add(test_record)
        session.commit()
        
        # Test model retrieval
        retrieved = session.query(CattleRecord).filter_by(lot_id='TEST001').first()
        print(f"   ✓ Record created and retrieved: {retrieved.lot_id}")
        
        # Cleanup
        session.delete(retrieved)
        session.commit()
        session.close()
        
        print("   ✓ Database operations successful")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Database Models test failed: {str(e)}")
        return False

def test_api_endpoints():
    """Test API endpoints (basic import test)"""
    print("🌐 Testing API Endpoints...")
    
    try:
        from api_server.api_router import create_app
        
        # Test that the FastAPI app can be created
        app = create_app()
        print(f"   ✓ FastAPI app created: {type(app).__name__}")
        
        # Test that routes are registered
        routes = [route.path for route in app.routes]
        expected_routes = ['/api/health', '/api/data', '/api/rules']
        
        for expected in expected_routes:
            if any(expected in route for route in routes):
                print(f"   ✓ Route found: {expected}")
            else:
                print(f"   ⚠️  Route not found: {expected}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ API Endpoints test failed: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🐄 DataHerd Core Functionality Test Suite")
    print("=" * 50)
    
    tests = [
        test_database_models,
        test_rule_manager,
        test_nlp_processor,
        test_data_processor,
        test_report_generator,
        test_api_endpoints
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()
        except Exception as e:
            print(f"   ❌ Test failed with exception: {str(e)}")
            print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! DataHerd is ready to use.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())

