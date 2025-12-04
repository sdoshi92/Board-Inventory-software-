import requests
import sys
import json
from datetime import datetime

class IssueRequestButtonTester:
    def __init__(self, base_url="https://boardventory.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.test_category_id = None
        self.test_boards = []

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
        """Set up test environment"""
        print("🔧 Setting up test environment for issue request button testing...")
        
        # 1. Register user
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"issue_button_test_{timestamp}@example.com"
        test_password = "IssueTest123!"
        
        result = self.run_api_test(
            "Setup - User Registration",
            "POST",
            "auth/register",
            200,
            data={"email": test_email, "password": test_password}
        )
        
        if not result or 'access_token' not in result:
            return False
            
        self.token = result['access_token']
        self.user_data = result['user']
        
        # 2. Create test category
        category_data = {
            "name": f"Issue Button Test Category {timestamp}",
            "description": "Category for issue request button testing",
            "manufacturer": "Test Manufacturer",
            "version": "1.0",
            "lead_time_days": 30,
            "minimum_stock_quantity": 5
        }
        
        result = self.run_api_test(
            "Setup - Create Category",
            "POST",
            "categories",
            200,
            data=category_data
        )
        
        if not result or 'id' not in result:
            return False
            
        self.test_category_id = result['id']
        
        # 3. Create test boards
        for i in range(5):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"ISSUE_BTN_{i+1:02d}_{timestamp}",
                "location": "In stock",
                "condition": "New",
                "qc_by": "Test QC Engineer",
                "comments": f"Issue button test board {i+1}"
            }
            
            result = self.run_api_test(
                f"Setup - Create Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if result and 'id' in result:
                self.test_boards.append({
                    'id': result['id'],
                    'serial_number': result['serial_number'],
                    'category_id': result['category_id']
                })
            else:
                return False
        
        print(f"✅ Test environment setup complete: {len(self.test_boards)} boards created")
        return True

    def test_single_issue_request_creation(self):
        """Test creating a single issue request (simulating issue request button click)"""
        if not self.test_category_id:
            return False
            
        # Test creating a single issue request
        request_data = {
            "category_id": self.test_category_id,
            "issued_to": "Single Request Test Engineer",
            "project_number": "SINGLE_REQ_001",
            "comments": "Testing single issue request creation via button"
        }
        
        result = self.run_api_test(
            "Issue Request Button - Single Request Creation",
            "POST",
            "issue-requests",
            200,
            data=request_data
        )
        
        if result:
            # Verify response structure
            required_fields = ['id', 'category_id', 'requested_by', 'issued_to', 'project_number', 'status', 'request_date_time']
            has_all_fields = all(field in result for field in required_fields)
            
            if not has_all_fields:
                self.log_test("Single Request Response Structure", False, f"Missing fields in response: {result}")
                return False
            
            # Verify response values
            if (result['category_id'] == self.test_category_id and 
                result['issued_to'] == "Single Request Test Engineer" and
                result['project_number'] == "SINGLE_REQ_001" and
                result['status'] == "pending"):
                
                return True
            else:
                self.log_test("Single Request Response Values", False, 
                    f"Response values don't match expected: {result}")
        
        return False

    def test_single_issue_request_with_specific_serial(self):
        """Test creating issue request with specific serial number"""
        if not self.test_category_id or not self.test_boards:
            return False
            
        # Use first test board's serial number
        specific_serial = self.test_boards[0]['serial_number']
        
        request_data = {
            "category_id": self.test_category_id,
            "serial_number": specific_serial,
            "issued_to": "Specific Serial Test Engineer",
            "project_number": "SPECIFIC_REQ_001",
            "comments": "Testing issue request with specific serial number"
        }
        
        result = self.run_api_test(
            "Issue Request Button - Specific Serial Request",
            "POST",
            "issue-requests",
            200,
            data=request_data
        )
        
        if result:
            # Verify the serial number is included in the response
            if result.get('serial_number') == specific_serial:
                return True
            else:
                self.log_test("Specific Serial Request Verification", False, 
                    f"Expected serial_number='{specific_serial}', got '{result.get('serial_number')}'")
        
        return False

    def test_bulk_issue_request_button_simulation(self):
        """Test bulk issue request creation (simulating bulk issue request button click)"""
        if not self.test_category_id:
            return False
            
        # Simulate clicking bulk issue request button with quantity
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "quantity": 2
                }
            ],
            "issued_to": "Bulk Button Test Engineer",
            "project_number": "BULK_BTN_001",
            "comments": "Testing bulk issue request button functionality"
        }
        
        result = self.run_api_test(
            "Issue Request Button - Bulk Request Creation",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        if result:
            # Verify response includes 'successful' field for frontend compatibility
            required_fields = ['message', 'request_id', 'total_boards', 'successful', 'boards']
            has_all_fields = all(field in result for field in required_fields)
            
            if not has_all_fields:
                self.log_test("Bulk Request Button Response Structure", False, f"Missing fields in response: {result}")
                return False
            
            # Verify 'successful' field specifically (mentioned in review request)
            if 'successful' in result and result['successful'] == 2:
                return True
            else:
                self.log_test("Bulk Request Button 'successful' Field", False, 
                    f"Expected successful=2, got successful={result.get('successful')}")
        
        return False

    def test_issue_request_retrieval_after_creation(self):
        """Test that created requests appear in the requests list"""
        # Get all issue requests
        result = self.run_api_test(
            "Issue Request Button - Retrieve Regular Requests",
            "GET",
            "issue-requests",
            200
        )
        
        if result and isinstance(result, list):
            # Look for our test requests
            test_requests = [req for req in result if 'REQ_001' in req.get('project_number', '')]
            
            if len(test_requests) >= 2:  # Should have at least 2 from our tests
                # Verify structure of returned requests
                for req in test_requests:
                    required_fields = ['id', 'category_id', 'requested_by', 'issued_to', 'project_number', 'status']
                    if not all(field in req for field in required_fields):
                        self.log_test("Request Retrieval Structure", False, f"Missing fields in request: {req}")
                        return False
                
                return True
            else:
                self.log_test("Request Retrieval Count", False, 
                    f"Expected at least 2 test requests, found {len(test_requests)}")
        
        return False

    def test_bulk_issue_request_retrieval_after_creation(self):
        """Test that bulk requests appear in bulk requests list"""
        result = self.run_api_test(
            "Issue Request Button - Retrieve Bulk Requests",
            "GET",
            "bulk-issue-requests",
            200
        )
        
        if result and isinstance(result, list):
            # Look for our test bulk requests
            test_bulk_requests = [req for req in result if 'BULK_BTN_001' in req.get('project_number', '')]
            
            if len(test_bulk_requests) >= 1:
                # Verify structure
                for req in test_bulk_requests:
                    required_fields = ['id', 'boards', 'requested_by', 'issued_to', 'project_number', 'status']
                    if not all(field in req for field in required_fields):
                        self.log_test("Bulk Request Retrieval Structure", False, f"Missing fields in bulk request: {req}")
                        return False
                    
                    # Verify boards array
                    if not isinstance(req['boards'], list) or len(req['boards']) == 0:
                        self.log_test("Bulk Request Boards Array", False, f"Invalid boards array in bulk request: {req['id']}")
                        return False
                
                return True
            else:
                self.log_test("Bulk Request Retrieval Count", False, 
                    f"Expected at least 1 test bulk request, found {len(test_bulk_requests)}")
        
        return False

    def test_error_scenarios_that_caused_user_issue(self):
        """Test error scenarios that might have caused the user's reported issue"""
        if not self.test_category_id:
            return False
            
        print("\n🔍 Testing error scenarios that might cause 'issue request button not creating requests'...")
        
        # Test 1: Invalid category ID (this might cause KeyError that was mentioned in test_result.md)
        invalid_request_data = {
            "category_id": "invalid-category-id-12345",
            "issued_to": "Error Test Engineer",
            "project_number": "ERROR_TEST_001",
            "comments": "Testing with invalid category ID"
        }
        
        result1 = self.run_api_test(
            "Error Scenario - Invalid Category ID",
            "POST",
            "issue-requests",
            400,  # Should return 400 error, not crash
            data=invalid_request_data
        )
        
        # Test 2: Bulk request with invalid category (this was the KeyError bug mentioned)
        bulk_invalid_data = {
            "categories": [
                {
                    "category_id": "invalid-category-id-12345",
                    "quantity": 1
                }
            ],
            "issued_to": "Bulk Error Test Engineer",
            "project_number": "BULK_ERROR_001",
            "comments": "Testing bulk request with invalid category"
        }
        
        result2 = self.run_api_test(
            "Error Scenario - Bulk Request Invalid Category",
            "POST",
            "issue-requests/bulk",
            400,  # Should return 400 error, not crash
            data=bulk_invalid_data
        )
        
        # Test 3: Empty request data
        empty_request_data = {}
        
        result3 = self.run_api_test(
            "Error Scenario - Empty Request Data",
            "POST",
            "issue-requests",
            422,  # Should return validation error
            data=empty_request_data
        )
        
        # Test 4: Missing required fields
        incomplete_request_data = {
            "category_id": self.test_category_id,
            # Missing issued_to and project_number
            "comments": "Testing incomplete request data"
        }
        
        result4 = self.run_api_test(
            "Error Scenario - Missing Required Fields",
            "POST",
            "issue-requests",
            422,  # Should return validation error
            data=incomplete_request_data
        )
        
        # All error scenarios should fail gracefully (return None from our test method)
        # This means the API handled the errors properly instead of crashing
        error_handling_working = (result1 is None and result2 is None and result3 is None and result4 is None)
        
        if error_handling_working:
            self.log_test("Error Scenarios Handling", True, "All error scenarios handled gracefully without crashes")
            return True
        else:
            self.log_test("Error Scenarios Handling", False, "Some error scenarios may not be handled properly")
            return False

    def test_authentication_scenarios(self):
        """Test authentication-related scenarios that might cause issues"""
        # Test without authentication token
        original_token = self.token
        self.token = None
        
        request_data = {
            "category_id": self.test_category_id,
            "issued_to": "Unauth Test Engineer",
            "project_number": "UNAUTH_001",
            "comments": "Testing without authentication"
        }
        
        result = self.run_api_test(
            "Authentication - Request Without Token",
            "POST",
            "issue-requests",
            401,  # Should return 401 unauthorized
            data=request_data
        )
        
        # Restore token
        self.token = original_token
        
        # Test with invalid token
        self.token = "invalid-token-12345"
        
        result2 = self.run_api_test(
            "Authentication - Request With Invalid Token",
            "POST",
            "issue-requests",
            401,  # Should return 401 unauthorized
            data=request_data
        )
        
        # Restore valid token
        self.token = original_token
        
        # Both should fail with 401 (which means they passed our test)
        return (result is None and result2 is None)

    def cleanup_test_environment(self):
        """Clean up test environment"""
        print("\n🧹 Cleaning up test environment...")
        
        # Clean up test boards
        for board in self.test_boards:
            self.run_api_test(
                f"Cleanup - Delete Board {board['id']}",
                "DELETE",
                f"boards/{board['id']}",
                200
            )
        
        # Clean up test category
        if self.test_category_id:
            self.run_api_test(
                "Cleanup - Delete Category",
                "DELETE",
                f"categories/{self.test_category_id}",
                200
            )
        
        print("✅ Cleanup complete")

    def run_all_tests(self):
        """Run all issue request button tests"""
        print("🚀 Testing Issue Request Button Functionality")
        print("🎯 Focus: Resolving 'When I hit issue request button it does not create any request for approval'")
        print("=" * 80)
        
        # Setup
        if not self.setup_test_environment():
            print("❌ Failed to set up test environment")
            return False
        
        # Run tests
        test_methods = [
            self.test_single_issue_request_creation,
            self.test_single_issue_request_with_specific_serial,
            self.test_bulk_issue_request_button_simulation,
            self.test_issue_request_retrieval_after_creation,
            self.test_bulk_issue_request_retrieval_after_creation,
            self.test_error_scenarios_that_caused_user_issue,
            self.test_authentication_scenarios
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test(f"Exception in {test_method.__name__}", False, f"Exception: {str(e)}")
        
        # Cleanup
        self.cleanup_test_environment()
        
        # Results
        print("\n" + "=" * 80)
        print("📊 ISSUE REQUEST BUTTON TEST RESULTS")
        print("=" * 80)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        # Show failed tests
        failed_tests = [result for result in self.test_results if not result['success']]
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  • {test['test_name']}: {test['details']}")
        else:
            print("\n✅ ALL TESTS PASSED!")
            print("🎉 Issue request button functionality is working correctly!")
            print("✅ The user's reported issue 'When I hit issue request button it does not create any request for approval' appears to be RESOLVED!")
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = IssueRequestButtonTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)