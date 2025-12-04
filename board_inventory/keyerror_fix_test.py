import requests
import json
from datetime import datetime

class KeyErrorFixTester:
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
        """Setup test user and category"""
        # Register user
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"keyerror_test_{timestamp}@example.com"
        test_password = "TestPass123!"
        
        result = self.run_api_test(
            "Setup - User Registration",
            "POST",
            "auth/register",
            200,
            data={"email": test_email, "password": test_password}
        )
        
        if result and 'access_token' in result:
            self.token = result['access_token']
            self.user_data = result['user']
        else:
            return False

        # Create test category
        category_data = {
            "name": f"KeyError Test Category {timestamp}",
            "description": "Test category for KeyError bug fix validation",
            "manufacturer": "Test Manufacturer",
            "version": "1.0",
            "lead_time_days": 30,
            "minimum_stock_quantity": 10
        }
        
        result = self.run_api_test(
            "Setup - Create Test Category",
            "POST",
            "categories",
            200,
            data=category_data
        )
        
        if result and 'id' in result:
            self.test_category_id = result['id']
            return True
        return False

    def test_single_issue_request(self):
        """Test 1: Single Issue Request (should work as before)"""
        if not hasattr(self, 'test_category_id'):
            return False

        # Create a test board first
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"SINGLE_TEST_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "New",
            "comments": "Board for single issue request test"
        }
        
        create_result = self.run_api_test(
            "Single Request - Create Test Board",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not create_result or 'id' not in create_result:
            return False

        # Create single issue request
        request_data = {
            "category_id": self.test_category_id,
            "issued_to": "Test Engineer",
            "project_number": "PROJ_SINGLE_001",
            "comments": "Single issue request test"
        }
        
        result = self.run_api_test(
            "Single Issue Request - Create Request",
            "POST",
            "issue-requests",
            200,
            data=request_data
        )
        
        if result and 'id' in result:
            # Clean up
            self.run_api_test(
                "Single Request - Cleanup Request",
                "DELETE",
                f"issue-requests/{result['id']}",
                200
            )
            self.run_api_test(
                "Single Request - Cleanup Board",
                "DELETE",
                f"boards/{create_result['id']}",
                200
            )
            return True
        return False

    def test_bulk_request_nonexistent_category(self):
        """Test 2: Bulk Issue Request with Non-existent Category (verify error message formats correctly without KeyError)"""
        
        # Use a fake category ID that doesn't exist
        fake_category_id = "nonexistent-category-id-12345"
        
        bulk_request_data = {
            "categories": [
                {
                    "category_id": fake_category_id,
                    "quantity": 2
                }
            ],
            "issued_to": "Test Engineer",
            "project_number": "PROJ_NONEXISTENT_001",
            "comments": "Testing nonexistent category handling"
        }
        
        result = self.run_api_test(
            "Bulk Request - Nonexistent Category",
            "POST",
            "issue-requests/bulk",
            400,  # Should return 400 error
            data=bulk_request_data
        )
        
        # The test passes if we get a 400 error (not a 500 KeyError)
        # The actual error message should be properly formatted
        return result is None  # None means we got the expected 400 status

    def test_bulk_request_valid_data(self):
        """Test 3: Bulk Issue Request with Valid Data (ensure successful bulk request creation works)"""
        if not hasattr(self, 'test_category_id'):
            return False

        # Create test boards for bulk request
        test_boards = []
        for i in range(3):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"BULK_VALID_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Bulk test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Bulk Valid - Create Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
            else:
                # Clean up created boards and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Bulk Valid Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False

        # Create bulk issue request
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "quantity": 2
                }
            ],
            "issued_to": "Bulk Test Engineer",
            "project_number": "PROJ_BULK_VALID_001",
            "comments": "Valid bulk issue request test"
        }
        
        result = self.run_api_test(
            "Bulk Request - Valid Data",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        success = False
        if result and 'created_requests' in result:
            created_requests = result['created_requests']
            if len(created_requests) == 2:  # Should create 2 requests
                success = True
                # Clean up created requests
                for request_info in created_requests:
                    self.run_api_test(
                        f"Bulk Valid Cleanup - Request {request_info['id']}",
                        "DELETE",
                        f"issue-requests/{request_info['id']}",
                        200
                    )

        # Clean up test boards
        for board_id in test_boards:
            self.run_api_test(f"Bulk Valid Final Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_error_response_format_validation(self):
        """Test 4: Error Response Format Validation (verify error messages display category names correctly)"""
        if not hasattr(self, 'test_category_id'):
            return False

        # Test with mix of valid and invalid categories
        fake_category_id = "fake-category-id-67890"
        
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,  # Valid category
                    "quantity": 1
                },
                {
                    "category_id": fake_category_id,  # Invalid category
                    "quantity": 1
                }
            ],
            "issued_to": "Error Format Test Engineer",
            "project_number": "PROJ_ERROR_FORMAT_001",
            "comments": "Testing error response format"
        }
        
        # This should return 200 with partial success (valid category works, invalid fails)
        result = self.run_api_test(
            "Error Format - Mixed Valid/Invalid Categories",
            "POST",
            "issue-requests/bulk",
            200,  # Should be partial success
            data=bulk_request_data
        )
        
        success = False
        if result:
            # Check if response has proper structure
            if ('created_requests' in result and 
                'failed_categories' in result and
                len(result['failed_categories']) > 0):
                
                # Verify failed category has proper error message format
                failed_category = result['failed_categories'][0]
                if ('category_id' in failed_category and 
                    'category_name' in failed_category and 
                    'error' in failed_category):
                    
                    # The key fix: category_name should be "Unknown" for nonexistent categories
                    # instead of causing a KeyError
                    if failed_category['category_name'] == 'Unknown':
                        success = True
                        
                        # Clean up any created requests
                        if 'created_requests' in result:
                            for request_info in result['created_requests']:
                                self.run_api_test(
                                    f"Error Format Cleanup - Request {request_info['id']}",
                                    "DELETE",
                                    f"issue-requests/{request_info['id']}",
                                    200
                                )
                    else:
                        self.log_test("Error Format Validation Details", False, 
                            f"Expected category_name='Unknown', got '{failed_category.get('category_name')}'")
                else:
                    self.log_test("Error Format Structure", False, 
                        f"Missing required fields in failed_categories: {failed_category}")
            else:
                self.log_test("Error Format Response Structure", False, 
                    f"Response missing expected fields: {result}")
        
        return success

    def test_partial_failure_handling(self):
        """Test 5: Partial Failures are handled properly"""
        if not hasattr(self, 'test_category_id'):
            return False

        # Create only 1 board but request 2 (should cause partial failure)
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"PARTIAL_TEST_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "New",
            "comments": "Board for partial failure test"
        }
        
        create_result = self.run_api_test(
            "Partial Failure - Create Single Board",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not create_result or 'id' not in create_result:
            return False

        # Request 2 boards when only 1 is available
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "quantity": 2  # More than available
                }
            ],
            "issued_to": "Partial Failure Test Engineer",
            "project_number": "PROJ_PARTIAL_001",
            "comments": "Testing partial failure handling"
        }
        
        result = self.run_api_test(
            "Partial Failure - Insufficient Stock",
            "POST",
            "issue-requests/bulk",
            400,  # Should fail completely due to insufficient stock
            data=bulk_request_data
        )
        
        # Clean up test board
        self.run_api_test(
            "Partial Failure - Cleanup Board",
            "DELETE",
            f"boards/{create_result['id']}",
            200
        )
        
        # Test passes if we get expected 400 error (not a KeyError crash)
        return result is None  # None means we got the expected 400 status

    def cleanup_test_environment(self):
        """Clean up test environment"""
        if hasattr(self, 'test_category_id'):
            self.run_api_test(
                "Cleanup - Delete Test Category",
                "DELETE",
                f"categories/{self.test_category_id}",
                200
            )

    def run_all_tests(self):
        """Run all KeyError fix validation tests"""
        print("🔧 Testing KeyError Bug Fix for Bulk Issue Requests")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_environment():
            print("❌ Failed to setup test environment")
            return False

        # Run tests in order
        tests = [
            ("Single Issue Request (baseline)", self.test_single_issue_request),
            ("Bulk Request with Nonexistent Category", self.test_bulk_request_nonexistent_category),
            ("Bulk Request with Valid Data", self.test_bulk_request_valid_data),
            ("Error Response Format Validation", self.test_error_response_format_validation),
            ("Partial Failure Handling", self.test_partial_failure_handling)
        ]
        
        for test_name, test_func in tests:
            print(f"\n🧪 Running: {test_name}")
            test_func()
        
        # Cleanup
        self.cleanup_test_environment()
        
        # Summary
        print("\n" + "=" * 60)
        print(f"📊 KeyError Fix Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("✅ All KeyError fix tests PASSED - Bug appears to be resolved!")
            return True
        else:
            print(f"❌ {self.tests_run - self.tests_passed} tests FAILED - KeyError bug may still exist")
            return False

if __name__ == "__main__":
    tester = KeyErrorFixTester()
    success = tester.run_all_tests()
    exit(0 if success else 1)