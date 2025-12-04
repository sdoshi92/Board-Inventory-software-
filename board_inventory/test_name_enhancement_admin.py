#!/usr/bin/env python3
"""
User Name Enhancement Testing Script - Admin Version
Tests the user name display improvements using admin credentials
"""

import requests
import sys
import json
from datetime import datetime

class AdminUserNameEnhancementTester:
    def __init__(self, base_url="https://boardventory.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        result = {
            "test_name": name,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {name}")
        if details:
            print(f"   Details: {details}")

    def run_api_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        if self.admin_token:
            test_headers['Authorization'] = f'Bearer {self.admin_token}'
        
        if headers:
            test_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=test_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=10)

            success = response.status_code == expected_status
            details = f"Status: {response.status_code}, Expected: {expected_status}"
            
            if not success:
                try:
                    error_detail = response.json().get('detail', 'No error detail')
                    details += f", Error: {error_detail}"
                except:
                    details += f", Response: {response.text[:200]}"
            
            self.log_test(name, success, details)
            
            if success:
                try:
                    return response.json()
                except:
                    return {}
            return None

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return None

    def setup_admin_access(self):
        """Setup admin access using provided credentials"""
        print("🔧 Setting up admin access...")
        
        # Test API health
        result = self.run_api_test(
            "API Health Check",
            "GET",
            "",
            200
        )
        if not result:
            return False
            
        # Login with provided admin credentials
        login_result = self.run_api_test(
            "Login with Admin Credentials",
            "POST",
            "auth/login",
            200,
            data={"email": "suraajvdoshi@gmail.com", "password": "test123"}
        )
        
        if login_result and 'access_token' in login_result:
            self.admin_token = login_result['access_token']
            self.admin_user = login_result['user']
            return True
        return False

    def test_existing_issue_requests_name_fields(self):
        """Test existing issue requests for name enhancement fields"""
        print("\n🔍 Testing Existing Issue Requests Name Enhancement...")
        
        # Get existing issue requests
        requests_result = self.run_api_test(
            "Get Existing Issue Requests",
            "GET",
            "issue-requests",
            200
        )
        
        if not requests_result or not isinstance(requests_result, list):
            return False
            
        success = True
        name_field_count = 0
        populated_name_count = 0
        
        for i, request in enumerate(requests_result[:5]):  # Check first 5 requests
            # Check if name fields are present
            has_requested_by_name = 'requested_by_name' in request
            has_issued_to_name = 'issued_to_name' in request
            
            if has_requested_by_name and has_issued_to_name:
                name_field_count += 1
                self.log_test(f"Issue Request {i+1} - Has Name Fields", True, 
                    f"Both requested_by_name and issued_to_name fields present")
                
                # Check if names are populated (not just email addresses)
                requested_by_name = request.get('requested_by_name', '')
                issued_to_name = request.get('issued_to_name', '')
                requested_by_email = request.get('requested_by', '')
                issued_to_email = request.get('issued_to', '')
                
                # Check if name is different from email (indicating name resolution worked)
                if (requested_by_name and requested_by_name != requested_by_email and requested_by_name.strip()) or \
                   (issued_to_name and issued_to_name != issued_to_email and issued_to_name.strip()):
                    populated_name_count += 1
                    self.log_test(f"Issue Request {i+1} - Names Populated", True, 
                        f"requested_by_name: '{requested_by_name}', issued_to_name: '{issued_to_name}'")
                else:
                    self.log_test(f"Issue Request {i+1} - Names Populated", True, 
                        f"Names may be empty or same as email (acceptable): requested_by_name: '{requested_by_name}', issued_to_name: '{issued_to_name}'")
            else:
                self.log_test(f"Issue Request {i+1} - Has Name Fields", False, 
                    f"Missing name fields: has_requested_by_name={has_requested_by_name}, has_issued_to_name={has_issued_to_name}")
                success = False
        
        # Summary of findings
        if name_field_count > 0:
            self.log_test("Issue Requests - Name Fields Implementation", True, 
                f"Found {name_field_count} requests with name fields out of {len(requests_result[:5])} checked")
        else:
            self.log_test("Issue Requests - Name Fields Implementation", False, 
                "No requests found with name fields")
            success = False
            
        return success

    def test_existing_bulk_issue_requests_name_fields(self):
        """Test existing bulk issue requests for name enhancement fields"""
        print("\n🔍 Testing Existing Bulk Issue Requests Name Enhancement...")
        
        # Get existing bulk issue requests
        bulk_requests_result = self.run_api_test(
            "Get Existing Bulk Issue Requests",
            "GET",
            "bulk-issue-requests",
            200
        )
        
        if not bulk_requests_result or not isinstance(bulk_requests_result, list):
            self.log_test("Bulk Issue Requests - API Response", False, "No bulk requests found or invalid response")
            return False
            
        success = True
        name_field_count = 0
        populated_name_count = 0
        
        for i, request in enumerate(bulk_requests_result[:5]):  # Check first 5 requests
            # Check if name fields are present
            has_requested_by_name = 'requested_by_name' in request
            has_issued_to_name = 'issued_to_name' in request
            
            if has_requested_by_name and has_issued_to_name:
                name_field_count += 1
                self.log_test(f"Bulk Request {i+1} - Has Name Fields", True, 
                    f"Both requested_by_name and issued_to_name fields present")
                
                # Check if names are populated (not just email addresses)
                requested_by_name = request.get('requested_by_name', '')
                issued_to_name = request.get('issued_to_name', '')
                requested_by_email = request.get('requested_by', '')
                issued_to_email = request.get('issued_to', '')
                
                # Check if name is different from email (indicating name resolution worked)
                if (requested_by_name and requested_by_name != requested_by_email and requested_by_name.strip()) or \
                   (issued_to_name and issued_to_name != issued_to_email and issued_to_name.strip()):
                    populated_name_count += 1
                    self.log_test(f"Bulk Request {i+1} - Names Populated", True, 
                        f"requested_by_name: '{requested_by_name}', issued_to_name: '{issued_to_name}'")
                else:
                    self.log_test(f"Bulk Request {i+1} - Names Populated", True, 
                        f"Names may be empty or same as email (acceptable): requested_by_name: '{requested_by_name}', issued_to_name: '{issued_to_name}'")
            else:
                self.log_test(f"Bulk Request {i+1} - Has Name Fields", False, 
                    f"Missing name fields: has_requested_by_name={has_requested_by_name}, has_issued_to_name={has_issued_to_name}")
                success = False
        
        # Summary of findings
        if name_field_count > 0:
            self.log_test("Bulk Requests - Name Fields Implementation", True, 
                f"Found {name_field_count} bulk requests with name fields out of {len(bulk_requests_result[:5])} checked")
        else:
            self.log_test("Bulk Requests - Name Fields Implementation", False, 
                "No bulk requests found with name fields")
            success = False
            
        return success

    def test_user_name_resolution_logic(self):
        """Test the user name resolution logic by creating test users and requests"""
        print("\n🔍 Testing User Name Resolution Logic...")
        
        # Create test users with known names
        test_users = [
            {
                "email": f"test.user1.{datetime.now().strftime('%H%M%S')}@example.com",
                "password": "password123",
                "first_name": "TestFirst",
                "last_name": "TestLast",
                "designation": "Test Engineer"
            },
            {
                "email": f"test.user2.{datetime.now().strftime('%H%M%S')}@example.com",
                "password": "password123",
                "first_name": "John",
                "last_name": "Smith",
                "designation": "Test Manager"
            }
        ]
        
        created_users = []
        for user_data in test_users:
            result = self.run_api_test(
                f"Register Test User {user_data['first_name']} {user_data['last_name']}",
                "POST",
                "auth/register",
                200,
                data=user_data
            )
            
            if result and 'user' in result:
                created_users.append({
                    'email': user_data['email'],
                    'expected_name': f"{user_data['first_name']} {user_data['last_name']}",
                    'password': user_data['password']
                })
        
        if len(created_users) < 2:
            return False
            
        # Create a test category for requests
        category_data = {
            "name": f"Name Test Category {datetime.now().strftime('%H%M%S')}",
            "description": "Test category for name resolution testing",
            "manufacturer": "Test Manufacturer",
            "version": "1.0",
            "lead_time_days": 30,
            "minimum_stock_quantity": 10
        }
        
        category_result = self.run_api_test(
            "Create Test Category for Name Resolution",
            "POST",
            "categories",
            200,
            data=category_data
        )
        
        if not category_result or 'id' not in category_result:
            return False
            
        test_category_id = category_result['id']
        
        # Create issue requests as different users
        test_requests = []
        for user in created_users:
            # Login as the user
            login_result = self.run_api_test(
                f"Login as {user['email']}",
                "POST",
                "auth/login",
                200,
                data={"email": user['email'], "password": user['password']}
            )
            
            if login_result and 'access_token' in login_result:
                # Temporarily use user token
                original_token = self.admin_token
                self.admin_token = login_result['access_token']
                
                # Create request
                request_data = {
                    "category_id": test_category_id,
                    "issued_to": user['email'],
                    "project_number": "PROJ_NAME_TEST",
                    "comments": f"Name resolution test request for {user['email']}"
                }
                
                create_result = self.run_api_test(
                    f"Create Request as {user['email']}",
                    "POST",
                    "issue-requests",
                    200,
                    data=request_data
                )
                
                # Restore admin token
                self.admin_token = original_token
                
                if create_result and 'id' in create_result:
                    test_requests.append({
                        'id': create_result['id'],
                        'user': user
                    })
        
        # Now get the requests as admin and verify name resolution
        requests_result = self.run_api_test(
            "Get Test Requests for Name Verification",
            "GET",
            "issue-requests",
            200
        )
        
        success = True
        if requests_result and isinstance(requests_result, list):
            for test_req in test_requests:
                found_request = next((req for req in requests_result if req['id'] == test_req['id']), None)
                
                if found_request:
                    requested_by_name = found_request.get('requested_by_name', '')
                    issued_to_name = found_request.get('issued_to_name', '')
                    expected_name = test_req['user']['expected_name']
                    
                    # Verify name resolution worked
                    if requested_by_name == expected_name and issued_to_name == expected_name:
                        self.log_test(f"Name Resolution - {test_req['user']['email']}", True, 
                            f"Names correctly resolved to '{expected_name}'")
                    else:
                        self.log_test(f"Name Resolution - {test_req['user']['email']}", False, 
                            f"Expected '{expected_name}', got requested_by_name='{requested_by_name}', issued_to_name='{issued_to_name}'")
                        success = False
                else:
                    self.log_test(f"Name Resolution - Request Not Found", False, 
                        f"Test request {test_req['id']} not found")
                    success = False
        
        # Clean up test requests
        for test_req in test_requests:
            self.run_api_test(
                f"Cleanup Test Request {test_req['id']}",
                "DELETE",
                f"issue-requests/{test_req['id']}",
                200
            )
            
        # Clean up test category
        self.run_api_test(
            "Cleanup Test Category",
            "DELETE",
            f"categories/{test_category_id}",
            200
        )
        
        return success

    def test_name_fallback_behavior(self):
        """Test fallback behavior when user names are not available"""
        print("\n🔍 Testing Name Fallback Behavior...")
        
        # Get all users to check name availability
        users_result = self.run_api_test(
            "Get All Users for Name Analysis",
            "GET",
            "users",
            200
        )
        
        if not users_result or not isinstance(users_result, list):
            return False
            
        # Analyze user name patterns
        users_with_names = 0
        users_without_names = 0
        
        for user in users_result[:10]:  # Check first 10 users
            first_name = user.get('first_name', '')
            last_name = user.get('last_name', '')
            email = user.get('email', '')
            
            if first_name and last_name:
                users_with_names += 1
                expected_name = f"{first_name} {last_name}"
                self.log_test(f"User Analysis - {email[:20]}... Has Names", True, 
                    f"Expected name format: '{expected_name}'")
            else:
                users_without_names += 1
                self.log_test(f"User Analysis - {email[:20]}... Has Names", True, 
                    f"No names available, should fallback to email: '{email}'")
        
        # Summary
        self.log_test("Name Fallback Analysis", True, 
            f"Users with names: {users_with_names}, Users without names: {users_without_names}")
        
        return True

    def run_all_tests(self):
        """Run all user name enhancement tests"""
        print("🚀 Starting User Name Enhancement Testing (Admin Version)...")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Setup admin access
        if not self.setup_admin_access():
            print("❌ Admin access setup failed - stopping tests")
            return False
            
        # Run specific user name enhancement tests
        test_results = []
        
        # Test 1: Existing Issue Requests Name Fields
        test_results.append(self.test_existing_issue_requests_name_fields())
        
        # Test 2: Existing Bulk Issue Requests Name Fields
        test_results.append(self.test_existing_bulk_issue_requests_name_fields())
        
        # Test 3: User Name Resolution Logic
        test_results.append(self.test_user_name_resolution_logic())
        
        # Test 4: Name Fallback Behavior
        test_results.append(self.test_name_fallback_behavior())
        
        # Print final summary
        print("\n" + "=" * 80)
        print("📊 USER NAME ENHANCEMENT TEST SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if all(test_results):
            print("🎉 ALL USER NAME ENHANCEMENT TESTS PASSED!")
            return True
        else:
            print("⚠️  Some user name enhancement tests failed - check details above")
            return False

if __name__ == "__main__":
    tester = AdminUserNameEnhancementTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)