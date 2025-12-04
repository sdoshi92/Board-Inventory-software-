#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class DashboardTester:
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
        """Setup test environment with user and category"""
        # Register user
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"dashboard_test_{timestamp}@example.com"
        test_password = "DashTest123!"
        
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
        
        # Make user admin
        admin_result = self.run_api_test(
            "Setup - Make Admin",
            "POST",
            f"setup-admin?email={test_email}",
            200
        )
        
        # Create test category
        category_data = {
            "name": f"Dashboard Test Category {timestamp}",
            "description": "Test category for dashboard functionality",
            "manufacturer": "Dashboard Test Manufacturer",
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
        
        if result and 'id' in result:
            self.test_category_id = result['id']
            return True
        return False

    def test_dashboard_data_endpoints(self):
        """Test dashboard data endpoints return correct data"""
        print("\n🔍 Testing Dashboard Data Endpoints")
        print("-" * 40)
        
        # Test GET /api/issue-requests
        requests_result = self.run_api_test(
            "Dashboard Data - GET /api/issue-requests",
            "GET",
            "issue-requests",
            200
        )
        
        if not requests_result or not isinstance(requests_result, list):
            return False
        
        # Test GET /api/bulk-issue-requests
        bulk_requests_result = self.run_api_test(
            "Dashboard Data - GET /api/bulk-issue-requests",
            "GET",
            "bulk-issue-requests",
            200
        )
        
        if not bulk_requests_result or not isinstance(bulk_requests_result, list):
            return False
        
        # Test GET /api/boards
        boards_result = self.run_api_test(
            "Dashboard Data - GET /api/boards",
            "GET",
            "boards",
            200
        )
        
        if not boards_result or not isinstance(boards_result, list):
            return False
        
        # Test GET /api/categories
        categories_result = self.run_api_test(
            "Dashboard Data - GET /api/categories",
            "GET",
            "categories",
            200
        )
        
        if not categories_result or not isinstance(categories_result, list):
            return False
        
        # Verify categories have minimum_stock_quantity field
        for category in categories_result:
            if 'minimum_stock_quantity' not in category:
                self.log_test("Dashboard Data - Categories Min Stock Field", False, 
                    f"Category missing minimum_stock_quantity field")
                return False
        
        return True

    def test_pending_requests_calculation(self):
        """Test pending requests calculation"""
        print("\n📋 Testing Pending Requests Calculation")
        print("-" * 40)
        
        # Create test issue requests with different statuses
        test_requests = []
        request_statuses = ['pending', 'approved', 'rejected', 'pending']
        
        for i, status in enumerate(request_statuses):
            request_data = {
                "category_id": self.test_category_id,
                "issued_to": f"Pending Test Engineer {i+1}",
                "project_number": f"PROJ_PENDING_{i+1}",
                "comments": f"Pending test request {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Pending Calc - Create Request {i+1}",
                "POST",
                "issue-requests",
                200,
                data=request_data
            )
            
            if create_result and 'id' in create_result:
                request_id = create_result['id']
                test_requests.append(request_id)
                
                # Update status if not pending
                if status != 'pending':
                    update_data = {"status": status}
                    self.run_api_test(
                        f"Pending Calc - Update Request {i+1} Status",
                        "PUT",
                        f"issue-requests/{request_id}",
                        200,
                        data=update_data
                    )
        
        # Create bulk issue requests
        # First create boards for bulk requests
        test_boards = []
        for i in range(3):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"PENDING_BULK_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New"
            }
            
            create_result = self.run_api_test(
                f"Pending Calc - Create Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
        
        # Create bulk requests with different statuses
        bulk_requests = []
        bulk_statuses = ['pending', 'approved']
        
        for i, status in enumerate(bulk_statuses):
            bulk_request_data = {
                "categories": [{"category_id": self.test_category_id, "quantity": 1}],
                "issued_to": f"Bulk Pending Test Engineer {i+1}",
                "project_number": f"PROJ_BULK_PENDING_{i+1}",
                "comments": f"Bulk pending test request {i+1}"
            }
            
            bulk_result = self.run_api_test(
                f"Pending Calc - Create Bulk Request {i+1}",
                "POST",
                "issue-requests/bulk",
                200,
                data=bulk_request_data
            )
            
            if bulk_result and 'request_id' in bulk_result:
                request_id = bulk_result['request_id']
                bulk_requests.append(request_id)
                
                # Update status if not pending
                if status != 'pending':
                    update_data = {"status": status}
                    self.run_api_test(
                        f"Pending Calc - Update Bulk Request {i+1} Status",
                        "PUT",
                        f"bulk-issue-requests/{request_id}",
                        200,
                        data=update_data
                    )
        
        # Verify pending counts
        requests_result = self.run_api_test(
            "Pending Calc - Get Issue Requests",
            "GET",
            "issue-requests",
            200
        )
        
        bulk_requests_result = self.run_api_test(
            "Pending Calc - Get Bulk Issue Requests",
            "GET",
            "bulk-issue-requests",
            200
        )
        
        if requests_result and bulk_requests_result:
            pending_count = sum(1 for req in requests_result if req.get('status') == 'pending')
            bulk_pending_count = sum(1 for req in bulk_requests_result if req.get('status') == 'pending')
            
            success = pending_count >= 2 and bulk_pending_count >= 1
            if not success:
                self.log_test("Pending Requests Count Verification", False, 
                    f"Expected at least 2 pending requests and 1 bulk pending, got {pending_count} and {bulk_pending_count}")
        else:
            success = False
        
        # Cleanup
        for req_id in test_requests:
            self.run_api_test(f"Pending Calc Cleanup - Request {req_id}", "DELETE", f"issue-requests/{req_id}", 200)
        for req_id in bulk_requests:
            self.run_api_test(f"Pending Calc Cleanup - Bulk Request {req_id}", "DELETE", f"bulk-issue-requests/{req_id}", 200)
        for board_id in test_boards:
            self.run_api_test(f"Pending Calc Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_repairing_boards_calculation(self):
        """Test repairing boards calculation"""
        print("\n🔧 Testing Repairing Boards Calculation")
        print("-" * 40)
        
        # Create test boards with different locations
        test_boards = []
        board_configs = [
            ("In stock", "New"),
            ("Repairing", "Needs repair"),
            ("Repairing", "Repaired"),
            ("Issued for machine", "New"),
            ("Repairing", "Scrap")
        ]
        
        for i, (location, condition) in enumerate(board_configs):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"REPAIR_CALC_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": location,
                "condition": condition,
                "comments": f"Repairing calc test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Repairing Calc - Create Board {i+1} ({location}/{condition})",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
        
        # Get boards and count repairing location
        boards_result = self.run_api_test(
            "Repairing Calc - Get Boards",
            "GET",
            "boards",
            200
        )
        
        success = False
        if boards_result:
            repairing_count = sum(1 for board in boards_result if board.get('location') == 'Repairing')
            expected_repairing = 3  # We created 3 boards in "Repairing" location
            
            success = repairing_count >= expected_repairing
            if not success:
                self.log_test("Repairing Boards Count Verification", False, 
                    f"Expected at least {expected_repairing} boards in repairing, found {repairing_count}")
        
        # Cleanup
        for board_id in test_boards:
            self.run_api_test(f"Repairing Calc Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_low_stock_categories_detection(self):
        """Test low stock categories detection"""
        print("\n📉 Testing Low Stock Categories Detection")
        print("-" * 40)
        
        # Create additional test categories with specific minimum_stock_quantity values
        test_categories = []
        category_configs = [
            ("Low Stock Category 1", 10),  # Will have 4 boards (below minimum)
            ("Low Stock Category 2", 3),   # Will have 4 boards (above minimum)
        ]
        
        for i, (name, min_stock) in enumerate(category_configs):
            category_data = {
                "name": f"{name} {datetime.now().strftime('%H%M%S')}",
                "description": f"Low stock test category {i+1}",
                "manufacturer": "Low Stock Test Manufacturer",
                "version": "1.0",
                "lead_time_days": 30,
                "minimum_stock_quantity": min_stock
            }
            
            create_result = self.run_api_test(
                f"Low Stock - Create Category {i+1}",
                "POST",
                "categories",
                200,
                data=category_data
            )
            
            if create_result and 'id' in create_result:
                test_categories.append((create_result['id'], min_stock))
        
        # Create boards for each test category
        test_boards = []
        for cat_id, min_stock in test_categories:
            # Create 4 boards per category: 2 in stock (New/Repaired), 1 in repairing (Repaired), 1 issued
            board_configs = [
                ("In stock", "New"),      # Counts towards stock
                ("In stock", "Repaired"), # Counts towards stock
                ("Repairing", "Repaired"), # Counts towards stock
                ("Issued for machine", "New") # Does NOT count towards stock
            ]
            
            for i, (location, condition) in enumerate(board_configs):
                board_data = {
                    "category_id": cat_id,
                    "serial_number": f"LOW_STOCK_{cat_id}_{i}_{datetime.now().strftime('%H%M%S')}",
                    "location": location,
                    "condition": condition,
                    "comments": f"Low stock test board for category {cat_id}"
                }
                
                create_result = self.run_api_test(
                    f"Low Stock - Create Board for Category {cat_id}",
                    "POST",
                    "boards",
                    200,
                    data=board_data
                )
                
                if create_result and 'id' in create_result:
                    test_boards.append(create_result['id'])
        
        # Get categories and boards to calculate stock
        categories_result = self.run_api_test(
            "Low Stock - Get Categories",
            "GET",
            "categories",
            200
        )
        
        boards_result = self.run_api_test(
            "Low Stock - Get Boards",
            "GET",
            "boards",
            200
        )
        
        success = False
        if categories_result and boards_result:
            # Calculate current stock for each test category
            low_stock_categories = []
            
            for cat_id, min_stock in test_categories:
                category_boards = [board for board in boards_result if board.get('category_id') == cat_id]
                
                # Current stock = In stock (New/Repaired) + Repairing (New/Repaired)
                current_stock = sum(1 for board in category_boards 
                                  if ((board.get('location') == 'In stock' and board.get('condition') in ['New', 'Repaired']) or
                                      (board.get('location') == 'Repairing' and board.get('condition') in ['New', 'Repaired'])))
                
                if current_stock < min_stock:
                    low_stock_categories.append(cat_id)
            
            # We expect 1 category to be low stock (min_stock 10, has 3 available boards)
            expected_low_stock_count = 1
            actual_low_stock_count = len(low_stock_categories)
            
            success = actual_low_stock_count == expected_low_stock_count
            if not success:
                self.log_test("Low Stock Categories Detection", False, 
                    f"Expected {expected_low_stock_count} low stock categories, found {actual_low_stock_count}")
        
        # Cleanup
        for board_id in test_boards:
            self.run_api_test(f"Low Stock Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        for cat_id, _ in test_categories:
            self.run_api_test(f"Low Stock Cleanup - Category {cat_id}", "DELETE", f"categories/{cat_id}", 200)
        
        return success

    def test_dashboard_stats_api(self):
        """Test dashboard stats API endpoint"""
        print("\n📊 Testing Dashboard Stats API")
        print("-" * 30)
        
        # Test GET /api/dashboard/stats endpoint
        stats_result = self.run_api_test(
            "Dashboard Stats - GET /api/dashboard/stats",
            "GET",
            "dashboard/stats",
            200
        )
        
        success = False
        if stats_result:
            # Verify all required fields are present
            required_fields = [
                'total_categories', 'total_boards', 'in_stock', 'issued', 
                'repaired', 'scrap', 'pending_requests'
            ]
            
            has_all_fields = all(field in stats_result for field in required_fields)
            if has_all_fields:
                # Verify field types are numeric
                all_numeric = all(isinstance(stats_result[field], int) for field in required_fields)
                if all_numeric:
                    # Verify logical consistency
                    if all(stats_result[field] >= 0 for field in required_fields):
                        success = True
                        self.log_test("Dashboard Stats API Response", True, 
                            f"All required fields present and valid: {stats_result}")
                    else:
                        self.log_test("Dashboard Stats Logical Consistency", False, 
                            f"Negative values found in stats: {stats_result}")
                else:
                    self.log_test("Dashboard Stats Field Types", False, 
                        f"Non-numeric values found in stats: {stats_result}")
            else:
                missing_fields = [field for field in required_fields if field not in stats_result]
                self.log_test("Dashboard Stats Required Fields", False, 
                    f"Missing required fields: {missing_fields}")
        
        return success

    def cleanup_test_environment(self):
        """Cleanup test environment"""
        if hasattr(self, 'test_category_id'):
            self.run_api_test(
                "Cleanup - Delete Category",
                "DELETE",
                f"categories/{self.test_category_id}",
                200
            )

    def run_dashboard_tests(self):
        """Run all dashboard tests"""
        print("🚀 Starting Enhanced Dashboard Functionality Tests")
        print("=" * 60)
        
        # Setup
        if not self.setup_test_environment():
            print("❌ Test environment setup failed. Stopping tests.")
            return False
        
        # Run dashboard tests
        test_results = []
        test_results.append(self.test_dashboard_data_endpoints())
        test_results.append(self.test_pending_requests_calculation())
        test_results.append(self.test_repairing_boards_calculation())
        test_results.append(self.test_low_stock_categories_detection())
        test_results.append(self.test_dashboard_stats_api())
        
        # Cleanup
        self.cleanup_test_environment()
        
        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Dashboard Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All dashboard tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} dashboard tests failed")
            return False

def main():
    """Main function to run dashboard tests"""
    tester = DashboardTester()
    success = tester.run_dashboard_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())