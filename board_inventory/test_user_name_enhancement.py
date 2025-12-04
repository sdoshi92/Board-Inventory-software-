#!/usr/bin/env python3
"""
User Name Enhancement Testing Script
Tests the user name display improvements in issue requests and bulk issue requests APIs
"""

import requests
import sys
import json
from datetime import datetime

class UserNameEnhancementTester:
    def __init__(self, base_url="https://boardventory.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_data = None
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
        
        if self.token:
            test_headers['Authorization'] = f'Bearer {self.token}'
        
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

    def setup_test_environment(self):
        """Set up test environment with user and category"""
        print("🔧 Setting up test environment...")
        
        # Test API health
        result = self.run_api_test(
            "API Health Check",
            "GET",
            "",
            200
        )
        if not result:
            return False
            
        # Register test user
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"name_test_user_{timestamp}@example.com"
        test_password = "TestPass123!"
        
        result = self.run_api_test(
            "Register Test User",
            "POST",
            "auth/register",
            200,
            data={
                "email": test_email, 
                "password": test_password,
                "first_name": "Test",
                "last_name": "User", 
                "designation": "Tester"
            }
        )
        
        if result and 'access_token' in result:
            self.token = result['access_token']
            self.user_data = result['user']
        else:
            return False
            
        # Create test category
        category_data = {
            "name": f"Name Test Category {timestamp}",
            "description": "Test category for name enhancement testing",
            "manufacturer": "Test Manufacturer",
            "version": "1.0",
            "lead_time_days": 30,
            "minimum_stock_quantity": 10
        }
        
        result = self.run_api_test(
            "Create Test Category",
            "POST",
            "categories",
            200,
            data=category_data
        )
        
        if result and 'id' in result:
            self.test_category_id = result['id']
            return True
        return False

    def test_issue_requests_name_enhancement(self):
        """Test user name enhancement in issue requests API"""
        print("\n🔍 Testing Issue Requests Name Enhancement...")
        
        # Create additional test users with different name configurations
        test_users = []
        user_configs = [
            ("John", "Doe", f"john.doe.{datetime.now().strftime('%H%M%S')}@example.com"),
            ("Jane", "Smith", f"jane.smith.{datetime.now().strftime('%H%M%S')}@example.com"),
        ]
        
        for first_name, last_name, email in user_configs:
            user_data = {
                "email": email,
                "password": "password123",
                "first_name": first_name,
                "last_name": last_name,
                "designation": "Test Engineer"
            }
            
            result = self.run_api_test(
                f"Register User {first_name} {last_name}",
                "POST",
                "auth/register",
                200,
                data=user_data
            )
            
            if result and 'user' in result:
                test_users.append({
                    'email': email,
                    'first_name': first_name,
                    'last_name': last_name,
                    'expected_name': f"{first_name} {last_name}",
                    'password': "password123"
                })
        
        if len(test_users) < 2:
            return False
            
        # Create issue requests with different users
        test_requests = []
        for i, user in enumerate(test_users):
            request_data = {
                "category_id": self.test_category_id,
                "issued_to": user['email'],
                "project_number": f"PROJ_NAME_{i+1}",
                "comments": f"Test request for user name enhancement {i+1}"
            }
            
            # Login as the user to create request
            login_result = self.run_api_test(
                f"Login as {user['first_name']} {user['last_name']}",
                "POST",
                "auth/login",
                200,
                data={"email": user['email'], "password": user['password']}
            )
            
            if login_result and 'access_token' in login_result:
                # Temporarily store current token
                original_token = self.token
                self.token = login_result['access_token']
                
                # Create request as this user
                create_result = self.run_api_test(
                    f"Create Request as {user['first_name']} {user['last_name']}",
                    "POST",
                    "issue-requests",
                    200,
                    data=request_data
                )
                
                # Restore original token
                self.token = original_token
                
                if create_result and 'id' in create_result:
                    test_requests.append({
                        'id': create_result['id'],
                        'requested_by': user['email'],
                        'issued_to': user['email'],
                        'expected_requested_by_name': user['expected_name'],
                        'expected_issued_to_name': user['expected_name']
                    })
        
        if len(test_requests) < 2:
            return False
            
        # Test GET /api/issue-requests includes name fields
        requests_result = self.run_api_test(
            "Get Issue Requests with Name Fields",
            "GET",
            "issue-requests",
            200
        )
        
        success = True
        if requests_result and isinstance(requests_result, list):
            # Find our test requests in the results
            for test_req in test_requests:
                found_request = next((req for req in requests_result if req['id'] == test_req['id']), None)
                
                if found_request:
                    # Check if name fields are present
                    if 'requested_by_name' not in found_request:
                        self.log_test("Issue Requests - requested_by_name Field Present", False, 
                            f"Missing requested_by_name field in request {test_req['id']}")
                        success = False
                        continue
                        
                    if 'issued_to_name' not in found_request:
                        self.log_test("Issue Requests - issued_to_name Field Present", False, 
                            f"Missing issued_to_name field in request {test_req['id']}")
                        success = False
                        continue
                    
                    # Check if names are populated correctly
                    actual_requested_by_name = found_request['requested_by_name']
                    actual_issued_to_name = found_request['issued_to_name']
                    
                    # Verify requested_by_name
                    if actual_requested_by_name == test_req['expected_requested_by_name']:
                        self.log_test("Issue Requests - requested_by_name Value Correct", True, 
                            f"Expected and got '{actual_requested_by_name}'")
                    else:
                        self.log_test("Issue Requests - requested_by_name Value Correct", False, 
                            f"Expected '{test_req['expected_requested_by_name']}', got '{actual_requested_by_name}'")
                        success = False
                    
                    # Verify issued_to_name
                    if actual_issued_to_name == test_req['expected_issued_to_name']:
                        self.log_test("Issue Requests - issued_to_name Value Correct", True, 
                            f"Expected and got '{actual_issued_to_name}'")
                    else:
                        self.log_test("Issue Requests - issued_to_name Value Correct", False, 
                            f"Expected '{test_req['expected_issued_to_name']}', got '{actual_issued_to_name}'")
                        success = False
                else:
                    self.log_test("Issue Requests - Request Found in API Response", False, 
                        f"Test request {test_req['id']} not found in API response")
                    success = False
        else:
            success = False
            
        # Clean up test requests
        for test_req in test_requests:
            self.run_api_test(
                f"Cleanup Request {test_req['id']}",
                "DELETE",
                f"issue-requests/{test_req['id']}",
                200
            )
            
        return success

    def test_bulk_issue_requests_name_enhancement(self):
        """Test user name enhancement in bulk issue requests API"""
        print("\n🔍 Testing Bulk Issue Requests Name Enhancement...")
        
        # Create test boards for bulk requests
        test_boards = []
        for i in range(3):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"BULK_NAME_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Bulk name test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Create Board {i+1} for Bulk Test",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
            else:
                return False
        
        # Create test users for bulk requests
        test_users = [
            ("Alice", "Johnson", f"alice.johnson.{datetime.now().strftime('%H%M%S')}@example.com"),
            ("Bob", "Wilson", f"bob.wilson.{datetime.now().strftime('%H%M%S')}@example.com")
        ]
        
        registered_users = []
        for first_name, last_name, email in test_users:
            user_data = {
                "email": email,
                "password": "password123",
                "first_name": first_name,
                "last_name": last_name,
                "designation": "Bulk Test Engineer"
            }
            
            result = self.run_api_test(
                f"Register Bulk User {first_name} {last_name}",
                "POST",
                "auth/register",
                200,
                data=user_data
            )
            
            if result and 'user' in result:
                registered_users.append({
                    'email': email,
                    'expected_name': f"{first_name} {last_name}",
                    'password': "password123"
                })
        
        if len(registered_users) < 2:
            return False
            
        # Create bulk issue requests
        test_bulk_requests = []
        for i, user in enumerate(registered_users):
            # Login as the user
            login_result = self.run_api_test(
                f"Login Bulk User {user['email']}",
                "POST",
                "auth/login",
                200,
                data={"email": user['email'], "password": user['password']}
            )
            
            if login_result and 'access_token' in login_result:
                # Temporarily store current token
                original_token = self.token
                self.token = login_result['access_token']
                
                # Create bulk request
                bulk_request_data = {
                    "categories": [
                        {
                            "category_id": self.test_category_id,
                            "quantity": 1
                        }
                    ],
                    "issued_to": user['email'],
                    "project_number": f"PROJ_BULK_NAME_{i+1}",
                    "comments": f"Bulk name test request {i+1}"
                }
                
                bulk_result = self.run_api_test(
                    f"Create Bulk Request as {user['email']}",
                    "POST",
                    "issue-requests/bulk",
                    200,
                    data=bulk_request_data
                )
                
                # Restore original token
                self.token = original_token
                
                if bulk_result and 'request_id' in bulk_result:
                    test_bulk_requests.append({
                        'id': bulk_result['request_id'],
                        'requested_by': user['email'],
                        'issued_to': user['email'],
                        'expected_requested_by_name': user['expected_name'],
                        'expected_issued_to_name': user['expected_name']
                    })
        
        if len(test_bulk_requests) < 2:
            return False
            
        # Test GET /api/bulk-issue-requests includes name fields
        bulk_requests_result = self.run_api_test(
            "Get Bulk Issue Requests with Name Fields",
            "GET",
            "bulk-issue-requests",
            200
        )
        
        success = True
        if bulk_requests_result and isinstance(bulk_requests_result, list):
            # Find our test bulk requests in the results
            for test_req in test_bulk_requests:
                found_request = next((req for req in bulk_requests_result if req['id'] == test_req['id']), None)
                
                if found_request:
                    # Check if name fields are present
                    if 'requested_by_name' not in found_request:
                        self.log_test("Bulk Requests - requested_by_name Field Present", False, 
                            f"Missing requested_by_name field in bulk request {test_req['id']}")
                        success = False
                        continue
                        
                    if 'issued_to_name' not in found_request:
                        self.log_test("Bulk Requests - issued_to_name Field Present", False, 
                            f"Missing issued_to_name field in bulk request {test_req['id']}")
                        success = False
                        continue
                    
                    # Check if names are populated correctly
                    actual_requested_by_name = found_request['requested_by_name']
                    actual_issued_to_name = found_request['issued_to_name']
                    
                    # Verify requested_by_name
                    if actual_requested_by_name == test_req['expected_requested_by_name']:
                        self.log_test("Bulk Requests - requested_by_name Value Correct", True, 
                            f"Expected and got '{actual_requested_by_name}'")
                    else:
                        self.log_test("Bulk Requests - requested_by_name Value Correct", False, 
                            f"Expected '{test_req['expected_requested_by_name']}', got '{actual_requested_by_name}'")
                        success = False
                    
                    # Verify issued_to_name
                    if actual_issued_to_name == test_req['expected_issued_to_name']:
                        self.log_test("Bulk Requests - issued_to_name Value Correct", True, 
                            f"Expected and got '{actual_issued_to_name}'")
                    else:
                        self.log_test("Bulk Requests - issued_to_name Value Correct", False, 
                            f"Expected '{test_req['expected_issued_to_name']}', got '{actual_issued_to_name}'")
                        success = False
                else:
                    self.log_test("Bulk Requests - Request Found in API Response", False, 
                        f"Test bulk request {test_req['id']} not found in API response")
                    success = False
        else:
            success = False
            
        # Clean up test bulk requests and boards
        for test_req in test_bulk_requests:
            self.run_api_test(
                f"Cleanup Bulk Request {test_req['id']}",
                "DELETE",
                f"bulk-issue-requests/{test_req['id']}",
                200
            )
        
        for board_id in test_boards:
            self.run_api_test(
                f"Cleanup Board {board_id}",
                "DELETE",
                f"boards/{board_id}",
                200
            )
            
        return success

    def test_name_format_validation(self):
        """Test that names are formatted as 'FirstName LastName'"""
        print("\n🔍 Testing Name Format Validation...")
        
        # Create a user with known names
        test_user_data = {
            "email": f"format.test.{datetime.now().strftime('%H%M%S')}@example.com",
            "password": "password123",
            "first_name": "TestFirst",
            "last_name": "TestLast",
            "designation": "Format Tester"
        }
        
        register_result = self.run_api_test(
            "Register User for Format Test",
            "POST",
            "auth/register",
            200,
            data=test_user_data
        )
        
        if not register_result or 'user' not in register_result:
            return False
            
        test_email = test_user_data['email']
        expected_name = "TestFirst TestLast"
        
        # Login as the test user
        login_result = self.run_api_test(
            "Login Format Test User",
            "POST",
            "auth/login",
            200,
            data={"email": test_email, "password": "password123"}
        )
        
        if not login_result or 'access_token' not in login_result:
            return False
            
        # Temporarily store current token
        original_token = self.token
        self.token = login_result['access_token']
        
        # Create an issue request
        request_data = {
            "category_id": self.test_category_id,
            "issued_to": test_email,
            "project_number": "PROJ_FORMAT_TEST",
            "comments": "Testing name format validation"
        }
        
        create_result = self.run_api_test(
            "Create Request for Format Test",
            "POST",
            "issue-requests",
            200,
            data=request_data
        )
        
        # Restore original token
        self.token = original_token
        
        if not create_result or 'id' not in create_result:
            return False
            
        request_id = create_result['id']
        
        # Get the request and verify name format
        requests_result = self.run_api_test(
            "Get Request for Format Verification",
            "GET",
            "issue-requests",
            200
        )
        
        success = False
        if requests_result and isinstance(requests_result, list):
            found_request = next((req for req in requests_result if req['id'] == request_id), None)
            
            if found_request:
                requested_by_name = found_request.get('requested_by_name', '')
                issued_to_name = found_request.get('issued_to_name', '')
                
                # Verify exact format "FirstName LastName"
                if requested_by_name == expected_name and issued_to_name == expected_name:
                    self.log_test("Name Format - FirstName LastName Format", True, 
                        f"Names correctly formatted as '{expected_name}'")
                    success = True
                else:
                    self.log_test("Name Format - FirstName LastName Format", False, 
                        f"Expected '{expected_name}', got requested_by_name='{requested_by_name}', issued_to_name='{issued_to_name}'")
        
        # Clean up
        self.run_api_test(
            "Cleanup Format Test Request",
            "DELETE",
            f"issue-requests/{request_id}",
            200
        )
        
        return success

    def test_existing_user_credentials(self):
        """Test with existing user credentials provided in review request"""
        print("\n🔍 Testing with Existing User Credentials...")
        
        # Test login with provided credentials
        login_result = self.run_api_test(
            "Login with Existing Credentials",
            "POST",
            "auth/login",
            200,
            data={"email": "suraajvdoshi@gmail.com", "password": "test123"}
        )
        
        if not login_result or 'access_token' not in login_result:
            return False
            
        # Store original token and use existing user token
        original_token = self.token
        self.token = login_result['access_token']
        
        # Get existing issue requests to verify name enhancement
        requests_result = self.run_api_test(
            "Get Existing Issue Requests",
            "GET",
            "issue-requests",
            200
        )
        
        success = True
        if requests_result and isinstance(requests_result, list) and len(requests_result) > 0:
            # Check first few requests for name fields
            for i, request in enumerate(requests_result[:3]):  # Check first 3 requests
                if 'requested_by_name' in request and 'issued_to_name' in request:
                    self.log_test(f"Existing Request {i+1} - Has Name Fields", True, 
                        f"requested_by_name: '{request['requested_by_name']}', issued_to_name: '{request['issued_to_name']}'")
                else:
                    self.log_test(f"Existing Request {i+1} - Has Name Fields", False, 
                        f"Missing name fields in existing request")
                    success = False
        else:
            self.log_test("Existing Requests - Found Requests", False, 
                "No existing requests found to test name enhancement")
            success = False
            
        # Get existing bulk issue requests to verify name enhancement
        bulk_requests_result = self.run_api_test(
            "Get Existing Bulk Issue Requests",
            "GET",
            "bulk-issue-requests",
            200
        )
        
        if bulk_requests_result and isinstance(bulk_requests_result, list) and len(bulk_requests_result) > 0:
            # Check first few bulk requests for name fields
            for i, request in enumerate(bulk_requests_result[:3]):  # Check first 3 requests
                if 'requested_by_name' in request and 'issued_to_name' in request:
                    self.log_test(f"Existing Bulk Request {i+1} - Has Name Fields", True, 
                        f"requested_by_name: '{request['requested_by_name']}', issued_to_name: '{request['issued_to_name']}'")
                else:
                    self.log_test(f"Existing Bulk Request {i+1} - Has Name Fields", False, 
                        f"Missing name fields in existing bulk request")
                    success = False
        else:
            self.log_test("Existing Bulk Requests - Found Requests", True, 
                "No existing bulk requests found (this is acceptable)")
            
        # Restore original token
        self.token = original_token
        
        return success

    def run_all_tests(self):
        """Run all user name enhancement tests"""
        print("🚀 Starting User Name Enhancement Testing...")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 80)
        
        # Setup test environment
        if not self.setup_test_environment():
            print("❌ Test environment setup failed - stopping tests")
            return False
            
        # Run specific user name enhancement tests
        test_results = []
        
        # Test 1: Issue Requests Name Enhancement
        test_results.append(self.test_issue_requests_name_enhancement())
        
        # Test 2: Bulk Issue Requests Name Enhancement
        test_results.append(self.test_bulk_issue_requests_name_enhancement())
        
        # Test 3: Name Format Validation
        test_results.append(self.test_name_format_validation())
        
        # Test 4: Existing User Credentials
        test_results.append(self.test_existing_user_credentials())
        
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
    tester = UserNameEnhancementTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)