#!/usr/bin/env python3
"""
Master test runner for Article-to-Audio project
Runs all tests in sequence and provides comprehensive report
"""

import subprocess
import sys
import os
from datetime import datetime

def run_test_script(script_name: str, description: str):
    """Run a test script and return success status"""
    print(f"\n{'='*80}")
    print(f"🧪 Running: {description}")
    print(f"📄 Script: {script_name}")
    print(f"⏰ Started: {datetime.now().strftime('%H:%M:%S')}")
    print('='*80)
    
    try:
        result = subprocess.run([
            'python3', script_name
        ], cwd='/Users/aettefagh/AI projects/claude-tools/article-to-audio-extension')
        
        success = result.returncode == 0
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"\n{status}: {description}")
        return success
        
    except Exception as e:
        print(f"❌ FAILED: {description} - {e}")
        return False

def main():
    """Run all test suites"""
    print("🚀 Article-to-Audio Comprehensive Test Suite")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Working Directory: /Users/aettefagh/AI projects/claude-tools/article-to-audio-extension")
    
    # Define test suites in order of execution
    test_suites = [
        # Phase 1: Infrastructure Tests
        ('verify_schema_execution.py', 'Supabase Schema Verification'),
        ('test_supabase_connection.py', 'Supabase Database Operations'),
        
        # Phase 2: Deployment Readiness  
        ('test_deployment.py', 'Deployment Readiness Checks'),
        
        # Phase 3: Integration Tests (requires running server)
        # Note: These require manual server startup
        # ('test_integration.py', 'FastAPI Integration Tests'),
    ]
    
    results = []
    
    # Run each test suite
    for script, description in test_suites:
        success = run_test_script(script, description)
        results.append((description, success))
    
    # Generate final report
    print(f"\n{'='*80}")
    print("📊 FINAL TEST REPORT")
    print(f"⏰ Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print('='*80)
    
    passed = 0
    failed = 0
    
    for description, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status}: {description}")
        if success:
            passed += 1
        else:
            failed += 1
    
    total = passed + failed
    print(f"\n📈 Summary: {passed}/{total} test suites passed ({failed} failed)")
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Ready for deployment!")
        print("\n🚀 Next Steps:")
        print("   1. Execute schema in Supabase SQL Editor (if not done)")
        print("   2. Start local server: python3 cloud-server.py")
        print("   3. Run integration tests: python3 test_integration.py")
        print("   4. Deploy to Render")
        print("   5. Test deployed service")
    else:
        print("⚠️ Some tests failed. Please review and fix issues before deployment.")
        print("\n🔧 Troubleshooting:")
        print("   1. Check Supabase schema execution")
        print("   2. Verify environment variables")
        print("   3. Install missing dependencies")
        print("   4. Review error messages above")
    
    print(f"\n📝 Test logs available in terminal output above")
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)