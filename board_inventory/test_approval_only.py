#!/usr/bin/env python3

import sys
import os
sys.path.append('/app')

from backend_test import ElectronicsInventoryAPITester

def main():
    tester = ElectronicsInventoryAPITester()
    
    print("🚀 Starting Bulk Issue Request Approval Tests Only")
    print("=" * 60)
    
    # Health check
    if not tester.test_health_check():
        print("❌ API is not accessible. Stopping tests.")
        return False
    
    # Authentication tests
    if not tester.test_user_registration():
        print("❌ User registration failed. Stopping tests.")
        return False
    
    # Category tests
    if not tester.test_create_category():
        print("❌ Category creation failed. Stopping tests.")
        return False
    
    # Run only the bulk issue request approval tests
    tester.run_bulk_issue_request_approval_tests()
    
    # Print results
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All bulk approval tests passed!")
        return True
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)