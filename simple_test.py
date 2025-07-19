#!/usr/bin/env python3
"""
DataHerd Simple Test Script
Basic functionality test without external API calls
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("📦 Testing Module Imports...")
    
    try:
        from dataherd.nlp_processor import NLPProcessor
        from dataherd.data_processor import DataProcessor
        from dataherd.rule_manager import RuleManager
        from dataherd.report_generator import ReportGenerator
        from db.models import CattleRecord
        from api_server.api_router import create_app
        
        print("   ✓ All modules imported successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Import test failed: {str(e)}")
        return False

def test_database():
    """Test database connection and basic operations"""
    print("🗄️  Testing Database...")
    
    try:
        from db.models import CattleRecord
        from db.base import SessionLocal
        from datetime import datetime
        
        session = SessionLocal()
        
        # Test record creation
        test_record = CattleRecord(
            lot_id='SIMPLE_TEST_001',
            weight=750.5,
            breed='Angus',
            birth_date=datetime(2023, 1, 15),
            health_status='healthy',
            feed_type='grain'
        )
        
        session.add(test_record)
        session.commit()
        
        # Test record retrieval
        retrieved = session.query(CattleRecord).filter_by(lot_id='SIMPLE_TEST_001').first()
        if retrieved:
            print(f"   ✓ Database operations successful: {retrieved.lot_id}")
            
            # Cleanup
            session.delete(retrieved)
            session.commit()
        else:
            print("   ❌ Failed to retrieve test record")
            return False
        
        session.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Database test failed: {str(e)}")
        return False

def test_core_classes():
    """Test that core classes can be instantiated"""
    print("🔧 Testing Core Classes...")
    
    try:
        from dataherd.nlp_processor import NLPProcessor
        from dataherd.data_processor import DataProcessor
        from dataherd.rule_manager import RuleManager
        from dataherd.report_generator import ReportGenerator
        
        # Test instantiation
        nlp = NLPProcessor()
        data_proc = DataProcessor()
        rule_mgr = RuleManager()
        report_gen = ReportGenerator()
        
        print("   ✓ All core classes instantiated successfully")
        return True
        
    except Exception as e:
        print(f"   ❌ Core classes test failed: {str(e)}")
        return False

def test_api_creation():
    """Test API app creation"""
    print("🌐 Testing API Creation...")
    
    try:
        from api_server.api_router import create_app
        
        app = create_app()
        print(f"   ✓ FastAPI app created: {type(app).__name__}")
        
        # Check some routes exist
        routes = [route.path for route in app.routes]
        print(f"   ✓ Found {len(routes)} routes")
        
        return True
        
    except Exception as e:
        print(f"   ❌ API creation test failed: {str(e)}")
        return False

def test_report_generation():
    """Test basic report generation"""
    print("📊 Testing Report Generation...")
    
    try:
        from dataherd.report_generator import ReportGenerator
        
        report_gen = ReportGenerator()
        
        # Test operation report (doesn't require external data)
        report = report_gen.generate_operation_report()
        
        if report and 'report_id' in report:
            print(f"   ✓ Report generated: {report['report_id']}")
            return True
        else:
            print("   ❌ Failed to generate report")
            return False
        
    except Exception as e:
        print(f"   ❌ Report generation test failed: {str(e)}")
        return False

def main():
    """Run simple tests"""
    print("🐄 DataHerd Simple Test Suite")
    print("=" * 40)
    
    tests = [
        test_imports,
        test_database,
        test_core_classes,
        test_api_creation,
        test_report_generation
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
    
    print("=" * 40)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All basic tests passed! DataHerd core functionality is working.")
        return 0
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit(main())

