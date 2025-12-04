import requests
import json
from datetime import datetime

class FinalKeyErrorTest:
    def __init__(self, base_url="https://boardventory.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.test_category_id = None
        self.results = []

    def log_result(self, test_name, passed, details=""):
        self.results.append({
            "test": test_name,
            "passed": passed,
            "details": details
        })
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")
        if details:
            print(f"   {details}")

    def setup(self):
        """Setup test environment"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"final_test_{timestamp}@example.com"
        test_password = "TestPass123!"
        
        # Register user
        response = requests.post(f"{self.api_url}/auth/register", json={
            "email": test_email, 
            "password": test_password
        })
        
        if response.status_code != 200:
            self.log_result("Setup - User Registration", False, f"Status: {response.status_code}")
            return False
        
        self.token = response.json()['access_token']
        self.headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        
        # Create test category
        category_data = {
            "name": f"Final Test Category {timestamp}",
            "description": "Final test category for KeyError validation",
            "manufacturer": "Test Manufacturer",
            "version": "1.0",
            "lead_time_days": 30,
            "minimum_stock_quantity": 10
        }
        
        response = requests.post(f"{self.api_url}/categories", json=category_data, headers=self.headers)
        if response.status_code == 200:
            self.test_category_id = response.json()['id']
            self.log_result("Setup - Create Test Category", True, f"Category ID: {self.test_category_id}")
            return True
        else:
            self.log_result("Setup - Create Test Category", False, f"Status: {response.status_code}")
            return False

    def test_1_single_issue_request(self):
        """Test 1: Single Issue Request (should work as before)"""
        # Create a test board
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"SINGLE_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "New",
            "comments": "Test board for single request"
        }
        
        response = requests.post(f"{self.api_url}/boards", json=board_data, headers=self.headers)
        if response.status_code != 200:
            self.log_result("Test 1 - Create Test Board", False, f"Status: {response.status_code}")
            return False
        
        board_id = response.json()['id']
        
        # Create single issue request
        request_data = {
            "category_id": self.test_category_id,
            "issued_to": "Test Engineer",
            "project_number": "PROJ_001",
            "comments": "Single issue request test"
        }
        
        response = requests.post(f"{self.api_url}/issue-requests", json=request_data, headers=self.headers)
        success = response.status_code == 200
        
        if success:
            request_id = response.json()['id']
            self.log_result("Test 1 - Single Issue Request", True, "Single request created successfully")
        else:
            self.log_result("Test 1 - Single Issue Request", False, f"Status: {response.status_code}, Error: {response.text}")
        
        # Cleanup board
        requests.delete(f"{self.api_url}/boards/{board_id}", headers=self.headers)
        
        return success

    def test_2_bulk_nonexistent_category(self):
        """Test 2: Bulk Issue Request with Non-existent Category"""
        bulk_request_data = {
            "categories": [
                {
                    "category_id": "nonexistent-category-id-12345",
                    "quantity": 2
                }
            ],
            "issued_to": "Test Engineer",
            "project_number": "PROJ_002",
            "comments": "Testing nonexistent category"
        }
        
        response = requests.post(f"{self.api_url}/issue-requests/bulk", json=bulk_request_data, headers=self.headers)
        
        # Should return 400 error with proper error message (no KeyError)
        success = response.status_code == 400
        
        if success:
            error_detail = response.json().get('detail', '')
            # Check that error message contains "Unknown" (not a KeyError)
            if "Unknown: Category not found" in error_detail:
                self.log_result("Test 2 - Bulk Nonexistent Category", True, f"Proper error message: {error_detail}")
            else:
                self.log_result("Test 2 - Bulk Nonexistent Category", False, f"Unexpected error format: {error_detail}")
                success = False
        else:
            self.log_result("Test 2 - Bulk Nonexistent Category", False, f"Status: {response.status_code}, Expected: 400")
        
        return success

    def test_3_bulk_valid_data(self):
        """Test 3: Bulk Issue Request with Valid Data"""
        # Create test boards
        board_ids = []
        for i in range(3):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"BULK_VALID_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Bulk test board {i+1}"
            }
            
            response = requests.post(f"{self.api_url}/boards", json=board_data, headers=self.headers)
            if response.status_code == 200:
                board_ids.append(response.json()['id'])
            else:
                self.log_result("Test 3 - Create Test Boards", False, f"Failed to create board {i+1}")
                return False
        
        # Create bulk request
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "quantity": 2
                }
            ],
            "issued_to": "Bulk Test Engineer",
            "project_number": "PROJ_003",
            "comments": "Valid bulk request test"
        }
        
        response = requests.post(f"{self.api_url}/issue-requests/bulk", json=bulk_request_data, headers=self.headers)
        success = response.status_code == 200
        
        if success:
            result = response.json()
            if 'created_requests' in result and len(result['created_requests']) == 2:
                self.log_result("Test 3 - Bulk Valid Data", True, f"Created {len(result['created_requests'])} requests successfully")
            else:
                self.log_result("Test 3 - Bulk Valid Data", False, f"Unexpected response structure: {result}")
                success = False
        else:
            self.log_result("Test 3 - Bulk Valid Data", False, f"Status: {response.status_code}, Error: {response.text}")
        
        # Cleanup boards
        for board_id in board_ids:
            requests.delete(f"{self.api_url}/boards/{board_id}", headers=self.headers)
        
        return success

    def test_4_error_response_format(self):
        """Test 4: Error Response Format Validation"""
        # Test with insufficient stock scenario
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "quantity": 5  # More than available (0 boards)
                }
            ],
            "issued_to": "Format Test Engineer",
            "project_number": "PROJ_004",
            "comments": "Testing error response format"
        }
        
        response = requests.post(f"{self.api_url}/issue-requests/bulk", json=bulk_request_data, headers=self.headers)
        
        # Should return 400 with proper error message format
        success = response.status_code == 400
        
        if success:
            error_detail = response.json().get('detail', '')
            # Check that category name is displayed correctly (not "Unknown" for existing category)
            if "Final Test Category" in error_detail and "Not enough boards available" in error_detail:
                self.log_result("Test 4 - Error Response Format", True, f"Proper error format: {error_detail}")
            else:
                self.log_result("Test 4 - Error Response Format", False, f"Unexpected error format: {error_detail}")
                success = False
        else:
            self.log_result("Test 4 - Error Response Format", False, f"Status: {response.status_code}, Expected: 400")
        
        return success

    def cleanup(self):
        """Cleanup test environment"""
        if self.test_category_id:
            response = requests.delete(f"{self.api_url}/categories/{self.test_category_id}", headers=self.headers)
            if response.status_code == 200:
                self.log_result("Cleanup - Delete Test Category", True, "Category deleted successfully")
            else:
                self.log_result("Cleanup - Delete Test Category", False, f"Status: {response.status_code}")

    def run_all_tests(self):
        """Run all tests for KeyError fix validation"""
        print("🔧 Final KeyError Bug Fix Validation")
        print("=" * 50)
        print("Focus: Quick validation that the KeyError fix resolved the 'When I press issue request, it goes in error' problem")
        print()
        
        if not self.setup():
            print("❌ Setup failed, cannot continue with tests")
            return False
        
        # Run the 4 specific tests from the review request
        tests = [
            ("Test 1: Single Issue Request (baseline)", self.test_1_single_issue_request),
            ("Test 2: Bulk Request with Nonexistent Category", self.test_2_bulk_nonexistent_category),
            ("Test 3: Bulk Request with Valid Data", self.test_3_bulk_valid_data),
            ("Test 4: Error Response Format Validation", self.test_4_error_response_format)
        ]
        
        print("Running tests...")
        print()
        
        for test_name, test_func in tests:
            print(f"🧪 {test_name}")
            test_func()
            print()
        
        self.cleanup()
        
        # Summary
        passed_tests = sum(1 for result in self.results if result['passed'])
        total_tests = len(self.results)
        
        print("=" * 50)
        print(f"📊 Final Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("✅ ALL TESTS PASSED - KeyError bug fix is working correctly!")
            print("✅ The 'When I press issue request, it goes in error' problem has been resolved.")
            return True
        else:
            print(f"❌ {total_tests - passed_tests} tests failed - KeyError bug may still exist")
            return False

if __name__ == "__main__":
    tester = FinalKeyErrorTest()
    success = tester.run_all_tests()
    exit(0 if success else 1)