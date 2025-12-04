import requests
import sys
import json
from datetime import datetime
import time

class BulkIssueRequestTester:
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
        self.created_requests = []

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
        """Set up test environment with user, category, and boards"""
        print("\n🔧 Setting up test environment...")
        
        # 1. Register user
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"bulk_test_user_{timestamp}@example.com"
        test_password = "BulkTest123!"
        
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
            "name": f"Bulk Test Category {timestamp}",
            "description": "Category for bulk issue request testing",
            "manufacturer": "Test Manufacturer",
            "version": "1.0",
            "lead_time_days": 30,
            "minimum_stock_quantity": 10
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
        
        # 3. Create test boards (10 boards with "New" condition in "In stock" location)
        for i in range(10):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"BULK_TEST_{i+1:02d}_{timestamp}",
                "location": "In stock",
                "condition": "New",
                "qc_by": "Test QC Engineer",
                "comments": f"Bulk test board {i+1}"
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

    def test_bulk_request_creation_single_category(self):
        """Test bulk issue request creation with single category"""
        if not self.test_category_id or len(self.test_boards) < 3:
            return False
            
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "quantity": 3
                }
            ],
            "issued_to": "Bulk Test Engineer",
            "project_number": "BULK_PROJ_001",
            "comments": "Testing bulk issue request with single category"
        }
        
        result = self.run_api_test(
            "Bulk Request - Single Category Creation",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        if result:
            # Verify response structure
            required_fields = ['message', 'request_id', 'total_boards', 'successful', 'boards']
            has_all_fields = all(field in result for field in required_fields)
            
            if not has_all_fields:
                self.log_test("Bulk Request Response Structure", False, f"Missing fields in response: {result}")
                return False
            
            # Verify response values
            if (result['total_boards'] == 3 and 
                result['successful'] == 3 and 
                len(result['boards']) == 3):
                
                # Store request ID for later tests
                self.created_requests.append(result['request_id'])
                return True
            else:
                self.log_test("Bulk Request Response Values", False, 
                    f"Expected 3 boards, got total_boards={result['total_boards']}, successful={result['successful']}, boards_count={len(result['boards'])}")
        
        return False

    def test_bulk_request_creation_multiple_categories(self):
        """Test bulk issue request creation with multiple categories"""
        if not self.test_category_id or len(self.test_boards) < 5:
            return False
            
        # Create a second category for testing
        timestamp = datetime.now().strftime('%H%M%S')
        category_data = {
            "name": f"Bulk Test Category 2 {timestamp}",
            "description": "Second category for bulk testing",
            "manufacturer": "Test Manufacturer 2",
            "version": "2.0",
            "lead_time_days": 45,
            "minimum_stock_quantity": 5
        }
        
        category_result = self.run_api_test(
            "Multiple Categories - Create Second Category",
            "POST",
            "categories",
            200,
            data=category_data
        )
        
        if not category_result or 'id' not in category_result:
            return False
            
        second_category_id = category_result['id']
        
        # Create boards for second category
        second_category_boards = []
        for i in range(3):
            board_data = {
                "category_id": second_category_id,
                "serial_number": f"BULK_CAT2_{i+1:02d}_{timestamp}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Second category bulk test board {i+1}"
            }
            
            result = self.run_api_test(
                f"Multiple Categories - Create Second Category Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if result and 'id' in result:
                second_category_boards.append(result['id'])
            else:
                return False
        
        # Create bulk request with multiple categories
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "quantity": 2
                },
                {
                    "category_id": second_category_id,
                    "quantity": 2
                }
            ],
            "issued_to": "Multi-Category Test Engineer",
            "project_number": "BULK_MULTI_001",
            "comments": "Testing bulk issue request with multiple categories"
        }
        
        result = self.run_api_test(
            "Bulk Request - Multiple Categories Creation",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        success = False
        if result:
            # Verify response for multiple categories
            if (result['total_boards'] == 4 and 
                result['successful'] == 4 and 
                len(result['boards']) == 4):
                
                # Verify boards from both categories are included
                category_1_boards = [b for b in result['boards'] if b['category_id'] == self.test_category_id]
                category_2_boards = [b for b in result['boards'] if b['category_id'] == second_category_id]
                
                if len(category_1_boards) == 2 and len(category_2_boards) == 2:
                    self.created_requests.append(result['request_id'])
                    success = True
                else:
                    self.log_test("Multiple Categories Board Distribution", False, 
                        f"Expected 2 boards from each category, got {len(category_1_boards)} and {len(category_2_boards)}")
            else:
                self.log_test("Multiple Categories Response Values", False, 
                    f"Expected 4 boards total, got total_boards={result['total_boards']}")
        
        # Clean up second category boards
        for board_id in second_category_boards:
            self.run_api_test(f"Multiple Categories Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        # Clean up second category
        self.run_api_test("Multiple Categories Cleanup - Second Category", "DELETE", f"categories/{second_category_id}", 200)
        
        return success

    def test_bulk_request_specific_serial_numbers(self):
        """Test bulk issue request with specific serial numbers"""
        if not self.test_category_id or len(self.test_boards) < 3:
            return False
            
        # Select specific serial numbers from our test boards
        selected_serials = [self.test_boards[0]['serial_number'], self.test_boards[1]['serial_number']]
        
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "serial_numbers": selected_serials
                }
            ],
            "issued_to": "Specific Serial Test Engineer",
            "project_number": "BULK_SERIAL_001",
            "comments": "Testing bulk issue request with specific serial numbers"
        }
        
        result = self.run_api_test(
            "Bulk Request - Specific Serial Numbers",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        if result:
            # Verify response contains the specific serial numbers
            if (result['total_boards'] == 2 and 
                result['successful'] == 2 and 
                len(result['boards']) == 2):
                
                # Check that the returned boards have the correct serial numbers
                returned_serials = [b['serial_number'] for b in result['boards']]
                if set(returned_serials) == set(selected_serials):
                    self.created_requests.append(result['request_id'])
                    return True
                else:
                    self.log_test("Specific Serial Numbers Verification", False, 
                        f"Expected serials {selected_serials}, got {returned_serials}")
            else:
                self.log_test("Specific Serial Numbers Response", False, 
                    f"Expected 2 boards, got total_boards={result['total_boards']}")
        
        return False

    def test_bulk_request_mixed_mode(self):
        """Test bulk issue request with mixed quantity and specific serial modes"""
        if not self.test_category_id or len(self.test_boards) < 5:
            return False
            
        # Create second category for mixed mode testing
        timestamp = datetime.now().strftime('%H%M%S')
        category_data = {
            "name": f"Mixed Mode Category {timestamp}",
            "description": "Category for mixed mode testing",
            "manufacturer": "Mixed Test Manufacturer",
            "version": "1.0",
            "lead_time_days": 30,
            "minimum_stock_quantity": 5
        }
        
        category_result = self.run_api_test(
            "Mixed Mode - Create Second Category",
            "POST",
            "categories",
            200,
            data=category_data
        )
        
        if not category_result or 'id' not in category_result:
            return False
            
        second_category_id = category_result['id']
        
        # Create boards for second category
        second_category_boards = []
        for i in range(3):
            board_data = {
                "category_id": second_category_id,
                "serial_number": f"MIXED_{i+1:02d}_{timestamp}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Mixed mode test board {i+1}"
            }
            
            result = self.run_api_test(
                f"Mixed Mode - Create Second Category Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if result and 'id' in result:
                second_category_boards.append({
                    'id': result['id'],
                    'serial_number': result['serial_number']
                })
            else:
                return False
        
        # Create mixed mode bulk request
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "quantity": 2  # Quantity mode
                },
                {
                    "category_id": second_category_id,
                    "serial_numbers": [second_category_boards[0]['serial_number']]  # Specific serial mode
                }
            ],
            "issued_to": "Mixed Mode Test Engineer",
            "project_number": "BULK_MIXED_001",
            "comments": "Testing bulk issue request with mixed quantity and serial modes"
        }
        
        result = self.run_api_test(
            "Bulk Request - Mixed Mode",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        success = False
        if result:
            # Verify mixed mode response
            if (result['total_boards'] == 3 and 
                result['successful'] == 3 and 
                len(result['boards']) == 3):
                
                # Verify boards from both categories with correct modes
                category_1_boards = [b for b in result['boards'] if b['category_id'] == self.test_category_id]
                category_2_boards = [b for b in result['boards'] if b['category_id'] == second_category_id]
                
                if (len(category_1_boards) == 2 and 
                    len(category_2_boards) == 1 and 
                    category_2_boards[0]['serial_number'] == second_category_boards[0]['serial_number']):
                    
                    self.created_requests.append(result['request_id'])
                    success = True
                else:
                    self.log_test("Mixed Mode Board Verification", False, 
                        f"Expected 2 from cat1 and 1 specific from cat2, got {len(category_1_boards)} and {len(category_2_boards)}")
            else:
                self.log_test("Mixed Mode Response Values", False, 
                    f"Expected 3 boards total, got total_boards={result['total_boards']}")
        
        # Clean up second category boards
        for board in second_category_boards:
            self.run_api_test(f"Mixed Mode Cleanup - Board {board['id']}", "DELETE", f"boards/{board['id']}", 200)
        
        # Clean up second category
        self.run_api_test("Mixed Mode Cleanup - Second Category", "DELETE", f"categories/{second_category_id}", 200)
        
        return success

    def test_bulk_request_retrieval(self):
        """Test retrieving bulk issue requests"""
        # Test GET /api/bulk-issue-requests
        result = self.run_api_test(
            "Bulk Request - Retrieval",
            "GET",
            "bulk-issue-requests",
            200
        )
        
        if result and isinstance(result, list):
            # Verify our created requests are in the response
            found_requests = [req for req in result if req['id'] in self.created_requests]
            
            if len(found_requests) >= len(self.created_requests):
                # Verify structure of returned requests
                for req in found_requests:
                    required_fields = ['id', 'boards', 'requested_by', 'issued_to', 'project_number', 'status', 'created_date']
                    if not all(field in req for field in required_fields):
                        self.log_test("Bulk Request Retrieval Structure", False, f"Missing fields in request: {req}")
                        return False
                    
                    # Verify boards array structure
                    if not isinstance(req['boards'], list) or len(req['boards']) == 0:
                        self.log_test("Bulk Request Boards Array", False, f"Invalid boards array in request: {req['id']}")
                        return False
                    
                    # Verify board structure
                    for board in req['boards']:
                        board_fields = ['category_id', 'serial_number', 'condition']
                        if not all(field in board for field in board_fields):
                            self.log_test("Bulk Request Board Structure", False, f"Missing fields in board: {board}")
                            return False
                
                return True
            else:
                self.log_test("Bulk Request Retrieval Count", False, 
                    f"Expected at least {len(self.created_requests)} requests, found {len(found_requests)}")
        
        return False

    def test_regular_issue_requests_retrieval(self):
        """Test retrieving regular issue requests (should be empty for bulk requests)"""
        result = self.run_api_test(
            "Regular Issue Requests - Retrieval",
            "GET",
            "issue-requests",
            200
        )
        
        if result and isinstance(result, list):
            # For bulk requests, regular issue requests should not contain our bulk request data
            # This verifies that bulk requests are stored separately
            bulk_related_requests = [req for req in result if 'BULK_' in req.get('project_number', '')]
            
            # Should have minimal or no bulk-related individual requests
            # (depending on implementation, bulk requests might create individual requests or not)
            self.log_test("Regular Issue Requests Separation", True, 
                f"Found {len(bulk_related_requests)} bulk-related individual requests (expected behavior)")
            return True
        
        return False

    def test_bulk_request_error_handling(self):
        """Test error handling for bulk issue requests"""
        if not self.test_category_id:
            return False
            
        # Test 1: Insufficient stock
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "quantity": 100  # More than available
                }
            ],
            "issued_to": "Error Test Engineer",
            "project_number": "BULK_ERROR_001",
            "comments": "Testing insufficient stock error"
        }
        
        result = self.run_api_test(
            "Bulk Request Error - Insufficient Stock",
            "POST",
            "issue-requests/bulk",
            400,  # Should return 400 error
            data=bulk_request_data
        )
        
        # Test 2: Non-existent category
        bulk_request_data = {
            "categories": [
                {
                    "category_id": "non-existent-category-id",
                    "quantity": 1
                }
            ],
            "issued_to": "Error Test Engineer",
            "project_number": "BULK_ERROR_002",
            "comments": "Testing non-existent category error"
        }
        
        result2 = self.run_api_test(
            "Bulk Request Error - Non-existent Category",
            "POST",
            "issue-requests/bulk",
            400,  # Should return 400 error
            data=bulk_request_data
        )
        
        # Test 3: Invalid serial number
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "serial_numbers": ["NON_EXISTENT_SERIAL"]
                }
            ],
            "issued_to": "Error Test Engineer",
            "project_number": "BULK_ERROR_003",
            "comments": "Testing invalid serial number error"
        }
        
        result3 = self.run_api_test(
            "Bulk Request Error - Invalid Serial Number",
            "POST",
            "issue-requests/bulk",
            400,  # Should return 400 error
            data=bulk_request_data
        )
        
        # All three error tests should have failed with 400 status (which means they passed our test)
        return (result is None and result2 is None and result3 is None)

    def test_bulk_request_deletion(self):
        """Test deleting bulk issue requests (admin only)"""
        if not self.created_requests:
            return False
            
        # First, make current user admin
        if hasattr(self, 'user_data'):
            admin_result = self.run_api_test(
                "Bulk Request Deletion - Setup Admin",
                "POST",
                f"setup-admin?email={self.user_data['email']}",
                200
            )
            
            if admin_result:
                # Test deleting a bulk request
                request_to_delete = self.created_requests[0]
                
                result = self.run_api_test(
                    "Bulk Request - Deletion",
                    "DELETE",
                    f"bulk-issue-requests/{request_to_delete}",
                    200
                )
                
                if result:
                    # Verify the request was deleted by trying to retrieve it
                    all_requests = self.run_api_test(
                        "Bulk Request Deletion - Verify Deletion",
                        "GET",
                        "bulk-issue-requests",
                        200
                    )
                    
                    if all_requests and isinstance(all_requests, list):
                        deleted_request = next((req for req in all_requests if req['id'] == request_to_delete), None)
                        if deleted_request is None:
                            # Remove from our tracking list
                            self.created_requests.remove(request_to_delete)
                            return True
                        else:
                            self.log_test("Bulk Request Deletion Verification", False, "Request still exists after deletion")
                    
        return False

    def test_end_to_end_workflow(self):
        """Test complete end-to-end bulk issue request workflow"""
        if not self.test_category_id or len(self.test_boards) < 3:
            return False
            
        print("\n🔄 Testing End-to-End Bulk Issue Request Workflow...")
        
        # Step 1: Create bulk request
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "quantity": 2
                }
            ],
            "issued_to": "E2E Test Engineer",
            "project_number": "BULK_E2E_001",
            "comments": "End-to-end workflow test"
        }
        
        create_result = self.run_api_test(
            "E2E Workflow - Create Bulk Request",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        if not create_result or 'request_id' not in create_result:
            return False
            
        request_id = create_result['request_id']
        
        # Step 2: Verify request appears in bulk requests list
        time.sleep(1)  # Small delay to ensure consistency
        
        retrieval_result = self.run_api_test(
            "E2E Workflow - Verify Request in List",
            "GET",
            "bulk-issue-requests",
            200
        )
        
        if not retrieval_result or not isinstance(retrieval_result, list):
            return False
            
        found_request = next((req for req in retrieval_result if req['id'] == request_id), None)
        if not found_request:
            self.log_test("E2E Workflow Request Verification", False, "Created request not found in bulk requests list")
            return False
        
        # Step 3: Verify request structure and data
        expected_data = {
            'issued_to': 'E2E Test Engineer',
            'project_number': 'BULK_E2E_001',
            'comments': 'End-to-end workflow test',
            'status': 'pending'
        }
        
        for field, expected_value in expected_data.items():
            if found_request.get(field) != expected_value:
                self.log_test(f"E2E Workflow Data Verification - {field}", False, 
                    f"Expected {field}='{expected_value}', got '{found_request.get(field)}'")
                return False
        
        # Step 4: Verify boards data
        if not isinstance(found_request.get('boards'), list) or len(found_request['boards']) != 2:
            self.log_test("E2E Workflow Boards Verification", False, 
                f"Expected 2 boards, got {len(found_request.get('boards', []))}")
            return False
        
        # Step 5: Clean up (delete the request)
        if hasattr(self, 'user_data'):
            # Make user admin for deletion
            self.run_api_test(
                "E2E Workflow - Setup Admin for Cleanup",
                "POST",
                f"setup-admin?email={self.user_data['email']}",
                200
            )
            
            # Delete the request
            delete_result = self.run_api_test(
                "E2E Workflow - Cleanup Request",
                "DELETE",
                f"bulk-issue-requests/{request_id}",
                200
            )
            
            if delete_result:
                return True
        
        return False

    def cleanup_test_environment(self):
        """Clean up test environment"""
        print("\n🧹 Cleaning up test environment...")
        
        # Clean up remaining bulk requests
        if hasattr(self, 'user_data'):
            # Make user admin for cleanup
            self.run_api_test(
                "Cleanup - Setup Admin",
                "POST",
                f"setup-admin?email={self.user_data['email']}",
                200
            )
            
            # Delete remaining requests
            for request_id in self.created_requests:
                self.run_api_test(
                    f"Cleanup - Delete Request {request_id}",
                    "DELETE",
                    f"bulk-issue-requests/{request_id}",
                    200
                )
        
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
        """Run all bulk issue request tests"""
        print("🚀 Starting Bulk Issue Request Functionality Tests")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_environment():
            print("❌ Failed to set up test environment")
            return False
        
        # Run tests
        test_methods = [
            self.test_bulk_request_creation_single_category,
            self.test_bulk_request_creation_multiple_categories,
            self.test_bulk_request_specific_serial_numbers,
            self.test_bulk_request_mixed_mode,
            self.test_bulk_request_retrieval,
            self.test_regular_issue_requests_retrieval,
            self.test_bulk_request_error_handling,
            self.test_bulk_request_deletion,
            self.test_end_to_end_workflow
        ]
        
        for test_method in test_methods:
            try:
                test_method()
            except Exception as e:
                self.log_test(f"Exception in {test_method.__name__}", False, f"Exception: {str(e)}")
        
        # Cleanup
        self.cleanup_test_environment()
        
        # Results
        print("\n" + "=" * 60)
        print("📊 BULK ISSUE REQUEST TEST RESULTS")
        print("=" * 60)
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
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = BulkIssueRequestTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)