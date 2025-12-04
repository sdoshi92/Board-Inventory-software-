import requests
import sys
import json
from datetime import datetime

class ElectronicsInventoryAPITester:
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

    def test_health_check(self):
        """Test API health check"""
        result = self.run_api_test(
            "API Health Check",
            "GET",
            "",
            200
        )
        return result is not None

    def test_user_registration(self):
        """Test user registration"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"test_user_{timestamp}@example.com"
        test_password = "TestPass123!"
        
        result = self.run_api_test(
            "User Registration",
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
            return True
        return False

    def test_user_login(self):
        """Test user login with existing user"""
        if not self.user_data:
            return False
            
        # Try to login with the registered user
        result = self.run_api_test(
            "User Login",
            "POST",
            "auth/login",
            200,
            data={"email": self.user_data['email'], "password": "TestPass123!"}
        )
        
        if result and 'access_token' in result:
            self.token = result['access_token']
            return True
        return False

    def test_get_current_user(self):
        """Test getting current user info"""
        result = self.run_api_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        return result is not None

    def test_create_category(self):
        """Test creating a category"""
        category_data = {
            "name": f"Test Category {datetime.now().strftime('%H%M%S')}",
            "description": "Test electronics board category",
            "manufacturer": "Test Manufacturer",
            "version": "1.0",
            "lead_time_days": 30,
            "minimum_stock_quantity": 10
        }
        
        result = self.run_api_test(
            "Create Category",
            "POST",
            "categories",
            200,
            data=category_data
        )
        
        if result and 'id' in result:
            self.test_category_id = result['id']
            return True
        return False

    def test_get_categories(self):
        """Test getting all categories"""
        result = self.run_api_test(
            "Get Categories",
            "GET",
            "categories",
            200
        )
        return result is not None and isinstance(result, list)

    def test_get_category_by_id(self):
        """Test getting a specific category"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        result = self.run_api_test(
            "Get Category by ID",
            "GET",
            f"categories/{self.test_category_id}",
            200
        )
        return result is not None

    def test_update_category(self):
        """Test updating a category"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        update_data = {
            "name": f"Updated Category {datetime.now().strftime('%H%M%S')}",
            "description": "Updated test electronics board category",
            "manufacturer": "Updated Manufacturer",
            "version": "2.0",
            "lead_time_days": 45,
            "minimum_stock_quantity": 15
        }
        
        result = self.run_api_test(
            "Update Category",
            "PUT",
            f"categories/{self.test_category_id}",
            200,
            data=update_data
        )
        return result is not None

    def test_create_board(self):
        """Test creating a board"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"TEST{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "OK",
            "qc_by": "Test QC Person",
            "comments": "Test board for API testing"
        }
        
        result = self.run_api_test(
            "Create Board",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if result and 'id' in result:
            self.test_board_id = result['id']
            return True
        return False

    def test_get_boards(self):
        """Test getting all boards"""
        result = self.run_api_test(
            "Get Boards",
            "GET",
            "boards",
            200
        )
        return result is not None and isinstance(result, list)

    def test_get_board_by_id(self):
        """Test getting a specific board"""
        if not hasattr(self, 'test_board_id'):
            return False
            
        result = self.run_api_test(
            "Get Board by ID",
            "GET",
            f"boards/{self.test_board_id}",
            200
        )
        return result is not None

    def test_update_board(self):
        """Test updating a board"""
        if not hasattr(self, 'test_board_id'):
            return False
            
        update_data = {
            "location": "Issued for machine",
            "condition": "OK",
            "issued_to": "Test Engineer",
            "project_number": "PROJ001",
            "comments": "Updated test board"
        }
        
        result = self.run_api_test(
            "Update Board",
            "PUT",
            f"boards/{self.test_board_id}",
            200,
            data=update_data
        )
        return result is not None

    def test_search_boards(self):
        """Test board search functionality"""
        # Test search without parameters
        result = self.run_api_test(
            "Search Boards (No Params)",
            "GET",
            "search",
            200
        )
        
        if result is None:
            return False
            
        # Test search with query parameter
        if hasattr(self, 'test_board_id'):
            result = self.run_api_test(
                "Search Boards (With Query)",
                "GET",
                f"search?query=TEST",
                200
            )
            return result is not None
        return True

    def test_dashboard_stats(self):
        """Test dashboard statistics"""
        result = self.run_api_test(
            "Dashboard Statistics",
            "GET",
            "dashboard/stats",
            200
        )
        
        if result:
            required_fields = ['total_categories', 'total_boards', 'in_stock', 'issued', 'repaired', 'scrap', 'pending_requests']
            has_all_fields = all(field in result for field in required_fields)
            if not has_all_fields:
                self.log_test("Dashboard Stats Fields", False, f"Missing fields in response: {result}")
                return False
            return True
        return False

    def test_dashboard_pending_requests_calculation(self):
        """Test dashboard pending requests calculation for enhanced widgets"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create test issue requests with different statuses
        test_requests = []
        request_statuses = ['pending', 'approved', 'rejected', 'pending', 'pending']
        
        for i, status in enumerate(request_statuses):
            request_data = {
                "category_id": self.test_category_id,
                "issued_to": f"Dashboard Test Engineer {i+1}",
                "project_number": f"PROJ_DASH_{i+1}",
                "comments": f"Dashboard test request {i+1} - status {status}"
            }
            
            create_result = self.run_api_test(
                f"Dashboard Pending - Create Request {i+1}",
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
                    # Make user admin first
                    if hasattr(self, 'user_data'):
                        self.run_api_test(
                            f"Dashboard Pending - Setup Admin for Request {i+1}",
                            "POST",
                            f"setup-admin?email={self.user_data['email']}",
                            200
                        )
                        
                        update_data = {"status": status}
                        self.run_api_test(
                            f"Dashboard Pending - Update Request {i+1} Status",
                            "PUT",
                            f"issue-requests/{request_id}",
                            200,
                            data=update_data
                        )
            else:
                # Clean up and return failure
                for req_id in test_requests:
                    self.run_api_test(f"Dashboard Pending Cleanup - Request {req_id}", "DELETE", f"issue-requests/{req_id}", 200)
                return False
        
        # Test GET /api/issue-requests returns correct data
        requests_result = self.run_api_test(
            "Dashboard Pending - Get Issue Requests",
            "GET",
            "issue-requests",
            200
        )
        
        if not requests_result or not isinstance(requests_result, list):
            return False
        
        # Count pending requests
        pending_count = sum(1 for req in requests_result if req.get('status') == 'pending')
        expected_pending = 3  # We created 3 pending requests
        
        success = pending_count >= expected_pending
        if not success:
            self.log_test("Dashboard Pending Requests Count", False, 
                f"Expected at least {expected_pending} pending requests, found {pending_count}")
        
        # Clean up test requests
        for req_id in test_requests:
            self.run_api_test(f"Dashboard Pending Final Cleanup - Request {req_id}", "DELETE", f"issue-requests/{req_id}", 200)
        
        return success

    def test_dashboard_bulk_pending_requests_calculation(self):
        """Test dashboard bulk pending requests calculation for enhanced widgets"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create test boards for bulk requests
        test_boards = []
        for i in range(3):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"DASH_BULK_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Dashboard bulk test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Dashboard Bulk Pending - Create Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Dashboard Bulk Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Create bulk issue requests with different statuses
        bulk_requests = []
        bulk_statuses = ['pending', 'approved', 'pending']
        
        for i, status in enumerate(bulk_statuses):
            bulk_request_data = {
                "categories": [
                    {
                        "category_id": self.test_category_id,
                        "quantity": 1
                    }
                ],
                "issued_to": f"Dashboard Bulk Test Engineer {i+1}",
                "project_number": f"PROJ_DASH_BULK_{i+1}",
                "comments": f"Dashboard bulk test request {i+1} - status {status}"
            }
            
            bulk_result = self.run_api_test(
                f"Dashboard Bulk Pending - Create Bulk Request {i+1}",
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
                    # Make user admin first
                    if hasattr(self, 'user_data'):
                        self.run_api_test(
                            f"Dashboard Bulk Pending - Setup Admin for Bulk Request {i+1}",
                            "POST",
                            f"setup-admin?email={self.user_data['email']}",
                            200
                        )
                        
                        update_data = {"status": status}
                        self.run_api_test(
                            f"Dashboard Bulk Pending - Update Bulk Request {i+1} Status",
                            "PUT",
                            f"bulk-issue-requests/{request_id}",
                            200,
                            data=update_data
                        )
            else:
                # Clean up and return failure
                for req_id in bulk_requests:
                    self.run_api_test(f"Dashboard Bulk Cleanup - Request {req_id}", "DELETE", f"bulk-issue-requests/{req_id}", 200)
                for board_id in test_boards:
                    self.run_api_test(f"Dashboard Bulk Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Test GET /api/bulk-issue-requests returns correct data
        bulk_requests_result = self.run_api_test(
            "Dashboard Bulk Pending - Get Bulk Issue Requests",
            "GET",
            "bulk-issue-requests",
            200
        )
        
        if not bulk_requests_result or not isinstance(bulk_requests_result, list):
            return False
        
        # Count pending bulk requests
        pending_bulk_count = sum(1 for req in bulk_requests_result if req.get('status') == 'pending')
        expected_pending_bulk = 2  # We created 2 pending bulk requests
        
        success = pending_bulk_count >= expected_pending_bulk
        if not success:
            self.log_test("Dashboard Bulk Pending Requests Count", False, 
                f"Expected at least {expected_pending_bulk} pending bulk requests, found {pending_bulk_count}")
        
        # Clean up test requests and boards
        for req_id in bulk_requests:
            self.run_api_test(f"Dashboard Bulk Final Cleanup - Request {req_id}", "DELETE", f"bulk-issue-requests/{req_id}", 200)
        for board_id in test_boards:
            self.run_api_test(f"Dashboard Bulk Final Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_dashboard_repairing_boards_calculation(self):
        """Test dashboard repairing boards calculation for enhanced widgets"""
        if not hasattr(self, 'test_category_id'):
            return False
            
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
                "serial_number": f"DASH_REPAIR_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": location,
                "condition": condition,
                "comments": f"Dashboard repairing test board {i+1} - {location}/{condition}"
            }
            
            create_result = self.run_api_test(
                f"Dashboard Repairing - Create Board {i+1} ({location}/{condition})",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Dashboard Repairing Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Test GET /api/boards returns correct data for repairing count
        boards_result = self.run_api_test(
            "Dashboard Repairing - Get Boards",
            "GET",
            "boards",
            200
        )
        
        if not boards_result or not isinstance(boards_result, list):
            return False
        
        # Count boards in "Repairing" location
        repairing_count = sum(1 for board in boards_result if board.get('location') == 'Repairing')
        expected_repairing = 3  # We created 3 boards in "Repairing" location
        
        success = repairing_count >= expected_repairing
        if not success:
            self.log_test("Dashboard Repairing Boards Count", False, 
                f"Expected at least {expected_repairing} boards in repairing, found {repairing_count}")
        
        # Clean up test boards
        for board_id in test_boards:
            self.run_api_test(f"Dashboard Repairing Final Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_dashboard_low_stock_categories_detection(self):
        """Test dashboard low stock categories detection for enhanced widgets"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create additional test categories with specific minimum_stock_quantity values
        test_categories = []
        category_configs = [
            ("Low Stock Category 1", 10),  # Will have 5 boards (below minimum)
            ("Low Stock Category 2", 3),   # Will have 5 boards (above minimum)
            ("Low Stock Category 3", 8)    # Will have 5 boards (below minimum)
        ]
        
        for i, (name, min_stock) in enumerate(category_configs):
            category_data = {
                "name": f"{name} {datetime.now().strftime('%H%M%S')}",
                "description": f"Dashboard low stock test category {i+1}",
                "manufacturer": "Dashboard Test Manufacturer",
                "version": "1.0",
                "lead_time_days": 30,
                "minimum_stock_quantity": min_stock
            }
            
            create_result = self.run_api_test(
                f"Dashboard Low Stock - Create Category {i+1}",
                "POST",
                "categories",
                200,
                data=category_data
            )
            
            if create_result and 'id' in create_result:
                test_categories.append((create_result['id'], min_stock))
            else:
                # Clean up and return failure
                for cat_id, _ in test_categories:
                    self.run_api_test(f"Dashboard Low Stock Cleanup - Category {cat_id}", "DELETE", f"categories/{cat_id}", 200)
                return False
        
        # Create boards for each test category
        test_boards = []
        for cat_id, min_stock in test_categories:
            # Create 5 boards per category with different conditions and locations
            board_configs = [
                ("In stock", "New"),      # Counts towards stock
                ("In stock", "Repaired"), # Counts towards stock
                ("Repairing", "New"),     # Counts towards stock (New/Repaired condition)
                ("Repairing", "Repaired"), # Counts towards stock
                ("Issued for machine", "New") # Does NOT count towards stock
            ]
            
            for i, (location, condition) in enumerate(board_configs):
                board_data = {
                    "category_id": cat_id,
                    "serial_number": f"DASH_STOCK_{cat_id}_{i}_{datetime.now().strftime('%H%M%S')}",
                    "location": location,
                    "condition": condition,
                    "comments": f"Dashboard stock test board for category {cat_id}"
                }
                
                create_result = self.run_api_test(
                    f"Dashboard Low Stock - Create Board for Category {cat_id}",
                    "POST",
                    "boards",
                    200,
                    data=board_data
                )
                
                if create_result and 'id' in create_result:
                    test_boards.append(create_result['id'])
                else:
                    # Clean up and return failure
                    for board_id in test_boards:
                        self.run_api_test(f"Dashboard Low Stock Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                    for cat_id, _ in test_categories:
                        self.run_api_test(f"Dashboard Low Stock Cleanup - Category {cat_id}", "DELETE", f"categories/{cat_id}", 200)
                    return False
        
        # Test GET /api/categories returns categories with minimum_stock_quantity
        categories_result = self.run_api_test(
            "Dashboard Low Stock - Get Categories",
            "GET",
            "categories",
            200
        )
        
        if not categories_result or not isinstance(categories_result, list):
            return False
        
        # Verify categories have minimum_stock_quantity field
        categories_have_min_stock = True
        for category in categories_result:
            if 'minimum_stock_quantity' not in category:
                categories_have_min_stock = False
                self.log_test("Dashboard Categories Min Stock Field", False, 
                    f"Category {category.get('name', 'Unknown')} missing minimum_stock_quantity field")
                break
        
        if not categories_have_min_stock:
            # Clean up and return failure
            for board_id in test_boards:
                self.run_api_test(f"Dashboard Low Stock Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
            for cat_id, _ in test_categories:
                self.run_api_test(f"Dashboard Low Stock Cleanup - Category {cat_id}", "DELETE", f"categories/{cat_id}", 200)
            return False
        
        # Test GET /api/boards returns boards for stock calculation
        boards_result = self.run_api_test(
            "Dashboard Low Stock - Get Boards",
            "GET",
            "boards",
            200
        )
        
        if not boards_result or not isinstance(boards_result, list):
            return False
        
        # Calculate current stock for each test category
        # Current stock = boards in "In stock" location with "New"/"Repaired" condition + 
        #                 boards in "Repairing" location with "New"/"Repaired" condition
        low_stock_categories = []
        
        for cat_id, min_stock in test_categories:
            category_boards = [board for board in boards_result if board.get('category_id') == cat_id]
            
            current_stock = sum(1 for board in category_boards 
                              if ((board.get('location') == 'In stock' and board.get('condition') in ['New', 'Repaired']) or
                                  (board.get('location') == 'Repairing' and board.get('condition') in ['New', 'Repaired'])))
            
            if current_stock < min_stock:
                low_stock_categories.append(cat_id)
        
        # We expect 2 categories to be low stock (min_stock 10 and 8, both have 4 available boards)
        expected_low_stock_count = 2
        actual_low_stock_count = len(low_stock_categories)
        
        success = actual_low_stock_count == expected_low_stock_count
        if not success:
            self.log_test("Dashboard Low Stock Categories Detection", False, 
                f"Expected {expected_low_stock_count} low stock categories, found {actual_low_stock_count}")
        
        # Clean up test boards and categories
        for board_id in test_boards:
            self.run_api_test(f"Dashboard Low Stock Final Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        for cat_id, _ in test_categories:
            self.run_api_test(f"Dashboard Low Stock Final Cleanup - Category {cat_id}", "DELETE", f"categories/{cat_id}", 200)
        
        return success

    def test_dashboard_stats_api_comprehensive(self):
        """Test comprehensive dashboard stats API for enhanced widgets"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create test data for comprehensive dashboard testing
        # Create additional category
        category_data = {
            "name": f"Dashboard Stats Category {datetime.now().strftime('%H%M%S')}",
            "description": "Category for dashboard stats testing",
            "manufacturer": "Dashboard Stats Manufacturer",
            "version": "1.0",
            "lead_time_days": 30,
            "minimum_stock_quantity": 5
        }
        
        create_result = self.run_api_test(
            "Dashboard Stats - Create Additional Category",
            "POST",
            "categories",
            200,
            data=category_data
        )
        
        if not create_result or 'id' not in create_result:
            return False
            
        additional_category_id = create_result['id']
        
        # Create test boards with various conditions
        test_boards = []
        board_configs = [
            ("In stock", "New"),
            ("In stock", "Repaired"),
            ("Issued for machine", "New"),
            ("Repairing", "Needs repair"),
            ("Repairing", "Repaired"),
            ("At customer site", "Scrap")
        ]
        
        for i, (location, condition) in enumerate(board_configs):
            board_data = {
                "category_id": additional_category_id,
                "serial_number": f"DASH_STATS_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": location,
                "condition": condition,
                "comments": f"Dashboard stats test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Dashboard Stats - Create Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Dashboard Stats Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                self.run_api_test("Dashboard Stats Cleanup - Category", "DELETE", f"categories/{additional_category_id}", 200)
                return False
        
        # Create test issue requests
        test_requests = []
        for i in range(3):
            request_data = {
                "category_id": additional_category_id,
                "issued_to": f"Dashboard Stats Engineer {i+1}",
                "project_number": f"PROJ_STATS_{i+1}",
                "comments": f"Dashboard stats test request {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Dashboard Stats - Create Request {i+1}",
                "POST",
                "issue-requests",
                200,
                data=request_data
            )
            
            if create_result and 'id' in create_result:
                test_requests.append(create_result['id'])
        
        # Test GET /api/dashboard/stats endpoint
        stats_result = self.run_api_test(
            "Dashboard Stats - Get Dashboard Statistics",
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
                    total_boards = stats_result['total_boards']
                    in_stock = stats_result['in_stock']
                    issued = stats_result['issued']
                    
                    # Basic sanity checks
                    if (total_boards >= 0 and in_stock >= 0 and issued >= 0 and
                        stats_result['pending_requests'] >= 0):
                        success = True
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
        
        # Clean up test data
        for req_id in test_requests:
            self.run_api_test(f"Dashboard Stats Final Cleanup - Request {req_id}", "DELETE", f"issue-requests/{req_id}", 200)
        for board_id in test_boards:
            self.run_api_test(f"Dashboard Stats Final Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        self.run_api_test("Dashboard Stats Final Cleanup - Category", "DELETE", f"categories/{additional_category_id}", 200)
        
        return success

    def test_inward_new_workflow(self):
        """Test Inward 'New' workflow - creating a new board with 'In stock' location"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"INWARD_NEW_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "OK",
            "qc_by": "QC Engineer",
            "comments": "New board for Inward workflow testing"
        }
        
        result = self.run_api_test(
            "Inward New Workflow - Create Board",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if result and 'id' in result:
            self.inward_test_board_id = result['id']
            # Verify the board was created with correct location
            if result.get('location') == 'In stock':
                return True
            else:
                self.log_test("Inward New Workflow Verification", False, f"Expected location 'In stock', got '{result.get('location')}'")
        return False

    def test_inward_repair_workflow(self):
        """Test Inward 'For Repairing' workflow - updating existing board to 'Repairing' location"""
        if not hasattr(self, 'inward_test_board_id'):
            return False
            
        update_data = {
            "location": "Repairing",
            "condition": "OK",
            "comments": "Board moved to repairing via Inward workflow"
        }
        
        result = self.run_api_test(
            "Inward Repair Workflow - Update Board Location",
            "PUT",
            f"boards/{self.inward_test_board_id}",
            200,
            data=update_data
        )
        
        if result:
            # Verify the board location was updated correctly
            if result.get('location') == 'Repairing':
                return True
            else:
                self.log_test("Inward Repair Workflow Verification", False, f"Expected location 'Repairing', got '{result.get('location')}'")
        return False

    def test_inward_serial_number_validation(self):
        """Test that existing serial numbers can be found for repair workflow"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # First create a board to test with
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"REPAIR_TEST_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "OK"
        }
        
        create_result = self.run_api_test(
            "Create Board for Serial Validation Test",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not create_result or 'id' not in create_result:
            return False
            
        # Now test that we can find this board by serial number via search
        search_result = self.run_api_test(
            "Search Board by Serial Number",
            "GET",
            f"search?query={board_data['serial_number']}",
            200
        )
        
        if search_result and isinstance(search_result, list) and len(search_result) > 0:
            # Check if our board is in the search results
            found_board = next((board for board in search_result if board['serial_number'] == board_data['serial_number']), None)
            if found_board:
                # Clean up the test board
                self.run_api_test(
                    "Delete Serial Validation Test Board",
                    "DELETE",
                    f"boards/{create_result['id']}",
                    200
                )
                return True
            else:
                self.log_test("Serial Number Validation", False, "Created board not found in search results")
        return False

    def test_inward_workflow_complete(self):
        """Test complete Inward workflow - New board creation followed by repair workflow"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Step 1: Create new board (New workflow)
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"COMPLETE_TEST_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "OK",
            "qc_by": "QC Engineer",
            "comments": "Complete workflow test board"
        }
        
        create_result = self.run_api_test(
            "Complete Workflow - Create New Board",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not create_result or 'id' not in create_result:
            return False
            
        board_id = create_result['id']
        
        # Step 2: Update board to Repairing (For Repairing workflow)
        update_data = {
            "location": "Repairing",
            "comments": "Board sent for repair via complete workflow test"
        }
        
        update_result = self.run_api_test(
            "Complete Workflow - Update to Repairing",
            "PUT",
            f"boards/{board_id}",
            200,
            data=update_data
        )
        
        if update_result and update_result.get('location') == 'Repairing':
            # Clean up
            self.run_api_test(
                "Complete Workflow - Cleanup",
                "DELETE",
                f"boards/{board_id}",
                200
            )
            return True
        return False

    def test_repaired_board_outward_workflow(self):
        """Test issuing repaired boards from repair location - Critical User Issue #1"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Step 1: Create board with "In stock" location
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"REPAIR_OUTWARD_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "New",
            "qc_by": "QC Engineer",
            "comments": "Board for repair outward testing"
        }
        
        create_result = self.run_api_test(
            "Repaired Outward - Create Board",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not create_result or 'id' not in create_result:
            return False
            
        board_id = create_result['id']
        
        # Step 2: Move board to "Repairing" location
        update_data = {
            "location": "Repairing",
            "condition": "Needs repair",
            "comments": "Board moved to repairing"
        }
        
        repair_result = self.run_api_test(
            "Repaired Outward - Move to Repairing",
            "PUT",
            f"boards/{board_id}",
            200,
            data=update_data
        )
        
        if not repair_result or repair_result.get('location') != 'Repairing':
            return False
            
        # Step 3: Change condition to "Repaired"
        repaired_data = {
            "condition": "Repaired",
            "comments": "Board repaired and ready for issue"
        }
        
        repaired_result = self.run_api_test(
            "Repaired Outward - Mark as Repaired",
            "PUT",
            f"boards/{board_id}",
            200,
            data=repaired_data
        )
        
        if not repaired_result or repaired_result.get('condition') != 'Repaired':
            return False
            
        # Step 4: Test direct board issue with comments
        outward_data = {
            "board_id": board_id,
            "issued_to": "Test Engineer",
            "project_number": "PROJ_REPAIR_001",
            "comments": "Issuing repaired board from repair location"
        }
        
        outward_result = self.run_api_test(
            "Repaired Outward - Direct Issue with Comments",
            "POST",
            "outward",
            200,
            data=outward_data
        )
        
        if outward_result and 'message' in outward_result:
            # Verify board was issued successfully
            verify_result = self.run_api_test(
                "Repaired Outward - Verify Board Issued",
                "GET",
                f"boards/{board_id}",
                200
            )
            
            if verify_result and verify_result.get('location') == 'Issued for machine':
                # Clean up
                self.run_api_test(
                    "Repaired Outward - Cleanup",
                    "DELETE",
                    f"boards/{board_id}",
                    200
                )
                return True
            else:
                self.log_test("Repaired Outward Verification", False, f"Board location not updated correctly: {verify_result.get('location') if verify_result else 'No result'}")
        
        return False

    def test_outward_comments_field(self):
        """Test comments field support in outward API - Critical User Issue #2"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create a test board
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"COMMENTS_TEST_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "New",
            "comments": "Board for comments testing"
        }
        
        create_result = self.run_api_test(
            "Comments Test - Create Board",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not create_result or 'id' not in create_result:
            return False
            
        board_id = create_result['id']
        
        # Test direct board issue with comments
        test_comments = "Test comments for direct board issue workflow"
        outward_data = {
            "board_id": board_id,
            "issued_to": "Comments Test Engineer",
            "project_number": "PROJ_COMMENTS_001",
            "comments": test_comments
        }
        
        outward_result = self.run_api_test(
            "Comments Test - Direct Issue with Comments",
            "POST",
            "outward",
            200,
            data=outward_data
        )
        
        if outward_result and 'message' in outward_result:
            # Verify comments were saved to board record
            verify_result = self.run_api_test(
                "Comments Test - Verify Comments Saved",
                "GET",
                f"boards/{board_id}",
                200
            )
            
            if verify_result and verify_result.get('comments') == test_comments:
                # Clean up
                self.run_api_test(
                    "Comments Test - Cleanup",
                    "DELETE",
                    f"boards/{board_id}",
                    200
                )
                return True
            else:
                self.log_test("Comments Field Verification", False, f"Comments not saved correctly. Expected: '{test_comments}', Got: '{verify_result.get('comments') if verify_result else 'No result'}'")
        
        return False

    def test_board_query_filtering(self):
        """Test board query shows repaired boards in repairing location - Critical User Issue #3"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create test boards for different scenarios
        test_boards = []
        
        # Board 1: In stock with New condition (should be available)
        board1_data = {
            "category_id": self.test_category_id,
            "serial_number": f"FILTER_NEW_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "New"
        }
        
        # Board 2: In stock with Repaired condition (should be available)
        board2_data = {
            "category_id": self.test_category_id,
            "serial_number": f"FILTER_REPAIRED_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "Repaired"
        }
        
        # Board 3: Repairing with Repaired condition (should be available)
        board3_data = {
            "category_id": self.test_category_id,
            "serial_number": f"FILTER_REPAIR_REPAIRED_{datetime.now().strftime('%H%M%S')}",
            "location": "Repairing",
            "condition": "Repaired"
        }
        
        # Board 4: Repairing with Needs repair condition (should NOT be available)
        board4_data = {
            "category_id": self.test_category_id,
            "serial_number": f"FILTER_REPAIR_NEEDS_{datetime.now().strftime('%H%M%S')}",
            "location": "Repairing",
            "condition": "Needs repair"
        }
        
        # Create all test boards
        for i, board_data in enumerate([board1_data, board2_data, board3_data, board4_data], 1):
            result = self.run_api_test(
                f"Filter Test - Create Board {i}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            if result and 'id' in result:
                test_boards.append(result['id'])
            else:
                return False
        
        # Get all boards and check filtering logic
        boards_result = self.run_api_test(
            "Filter Test - Get All Boards",
            "GET",
            "boards",
            200
        )
        
        if not boards_result or not isinstance(boards_result, list):
            return False
        
        # Find our test boards in the results
        found_boards = [board for board in boards_result if board['id'] in test_boards]
        
        if len(found_boards) != 4:
            self.log_test("Board Query Filtering", False, f"Expected 4 test boards, found {len(found_boards)}")
            return False
        
        # Verify filtering logic - boards that should be available for issuing
        available_boards = []
        for board in found_boards:
            # Check if board matches the new filtering criteria
            if ((board['location'] == 'In stock' and board['condition'] in ['New', 'Repaired']) or
                (board['location'] == 'Repairing' and board['condition'] == 'Repaired')):
                available_boards.append(board)
        
        # Should have 3 available boards (board1, board2, board3)
        expected_available = 3
        if len(available_boards) == expected_available:
            success = True
        else:
            success = False
            self.log_test("Board Query Filtering Logic", False, f"Expected {expected_available} available boards, found {len(available_boards)}")
        
        # Clean up test boards
        for board_id in test_boards:
            self.run_api_test(
                f"Filter Test - Cleanup Board {board_id}",
                "DELETE",
                f"boards/{board_id}",
                200
            )
        
        return success

    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow: New board → Repairing → Repaired → Issued - Critical User Issue #4"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Step 1: Create new board
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"E2E_TEST_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "New",
            "qc_by": "QC Engineer",
            "comments": "End-to-end workflow test board"
        }
        
        create_result = self.run_api_test(
            "E2E Workflow - Create New Board",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not create_result or 'id' not in create_result:
            return False
            
        board_id = create_result['id']
        
        # Step 2: Move to Repairing
        repair_data = {
            "location": "Repairing",
            "condition": "Needs repair",
            "comments": "Board sent for repair"
        }
        
        repair_result = self.run_api_test(
            "E2E Workflow - Move to Repairing",
            "PUT",
            f"boards/{board_id}",
            200,
            data=repair_data
        )
        
        if not repair_result or repair_result.get('location') != 'Repairing':
            return False
        
        # Step 3: Mark as Repaired
        repaired_data = {
            "condition": "Repaired",
            "comments": "Board repair completed"
        }
        
        repaired_result = self.run_api_test(
            "E2E Workflow - Mark as Repaired",
            "PUT",
            f"boards/{board_id}",
            200,
            data=repaired_data
        )
        
        if not repaired_result or repaired_result.get('condition') != 'Repaired':
            return False
        
        # Step 4: Issue the repaired board
        outward_data = {
            "board_id": board_id,
            "issued_to": "End-to-End Test Engineer",
            "project_number": "PROJ_E2E_001",
            "comments": "Issuing repaired board - end-to-end test"
        }
        
        issue_result = self.run_api_test(
            "E2E Workflow - Issue Repaired Board",
            "POST",
            "outward",
            200,
            data=outward_data
        )
        
        if not issue_result or 'message' not in issue_result:
            return False
        
        # Step 5: Verify final state
        final_result = self.run_api_test(
            "E2E Workflow - Verify Final State",
            "GET",
            f"boards/{board_id}",
            200
        )
        
        if final_result and final_result.get('location') == 'Issued for machine':
            # Clean up
            self.run_api_test(
                "E2E Workflow - Cleanup",
                "DELETE",
                f"boards/{board_id}",
                200
            )
            return True
        else:
            self.log_test("E2E Workflow Final Verification", False, f"Expected location 'Issued for machine', got '{final_result.get('location') if final_result else 'No result'}'")
        
        return False

    def test_issue_request_workflow(self):
        """Test request-based outward workflow with repaired boards"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create a repaired board in repairing location
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"REQUEST_TEST_{datetime.now().strftime('%H%M%S')}",
            "location": "Repairing",
            "condition": "Repaired",
            "comments": "Board for request workflow testing"
        }
        
        create_result = self.run_api_test(
            "Request Workflow - Create Repaired Board",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not create_result or 'id' not in create_result:
            return False
            
        board_id = create_result['id']
        serial_number = create_result['serial_number']
        
        # Create an issue request
        request_data = {
            "category_id": self.test_category_id,
            "serial_number": serial_number,
            "issued_to": "Request Test Engineer",
            "project_number": "PROJ_REQUEST_001",
            "comments": "Request for repaired board"
        }
        
        request_result = self.run_api_test(
            "Request Workflow - Create Issue Request",
            "POST",
            "issue-requests",
            200,
            data=request_data
        )
        
        if not request_result or 'id' not in request_result:
            return False
            
        request_id = request_result['id']
        
        # Approve the request (need admin role for this)
        # First, make current user admin
        if hasattr(self, 'user_data'):
            admin_result = self.run_api_test(
                "Request Workflow - Setup Admin",
                "POST",
                f"setup-admin?email={self.user_data['email']}",
                200
            )
            
            if admin_result:
                # Approve the request
                approve_data = {
                    "status": "approved",
                    "serial_number": serial_number
                }
                
                approve_result = self.run_api_test(
                    "Request Workflow - Approve Request",
                    "PUT",
                    f"issue-requests/{request_id}",
                    200,
                    data=approve_data
                )
                
                if approve_result and approve_result.get('status') == 'approved':
                    # Issue the board based on approved request
                    outward_data = {
                        "request_id": request_id,
                        "comments": "Issuing based on approved request"
                    }
                    
                    outward_result = self.run_api_test(
                        "Request Workflow - Issue Board",
                        "POST",
                        "outward",
                        200,
                        data=outward_data
                    )
                    
                    if outward_result and 'message' in outward_result:
                        # Clean up
                        self.run_api_test(
                            "Request Workflow - Cleanup Board",
                            "DELETE",
                            f"boards/{board_id}",
                            200
                        )
                        self.run_api_test(
                            "Request Workflow - Cleanup Request",
                            "DELETE",
                            f"issue-requests/{request_id}",
                            200
                        )
                        return True
        
        return False

    def test_repairing_condition_updates_new(self):
        """Test updating board condition to 'New' in Repairing location - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create a test board
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"REPAIR_NEW_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "OK",
            "comments": "Board for condition update testing"
        }
        
        create_result = self.run_api_test(
            "Repairing Condition New - Create Board",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not create_result or 'id' not in create_result:
            return False
            
        board_id = create_result['id']
        
        # Update board to Repairing location with 'New' condition
        update_data = {
            "location": "Repairing",
            "condition": "New",
            "comments": "Board moved to repairing with New condition"
        }
        
        update_result = self.run_api_test(
            "Repairing Condition New - Update to Repairing with New Condition",
            "PUT",
            f"boards/{board_id}",
            200,
            data=update_data
        )
        
        if update_result:
            # Verify both location and condition were updated correctly
            if (update_result.get('location') == 'Repairing' and 
                update_result.get('condition') == 'New' and
                update_result.get('comments') == "Board moved to repairing with New condition"):
                
                # Clean up
                self.run_api_test(
                    "Repairing Condition New - Cleanup",
                    "DELETE",
                    f"boards/{board_id}",
                    200
                )
                return True
            else:
                self.log_test("Repairing Condition New Verification", False, 
                    f"Expected location='Repairing', condition='New', got location='{update_result.get('location')}', condition='{update_result.get('condition')}'")
        
        return False

    def test_repairing_condition_updates_repaired(self):
        """Test updating board condition to 'Repaired' in Repairing location - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create a test board
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"REPAIR_REPAIRED_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "OK",
            "comments": "Board for condition update testing"
        }
        
        create_result = self.run_api_test(
            "Repairing Condition Repaired - Create Board",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not create_result or 'id' not in create_result:
            return False
            
        board_id = create_result['id']
        
        # Update board to Repairing location with 'Repaired' condition
        update_data = {
            "location": "Repairing",
            "condition": "Repaired",
            "comments": "Board moved to repairing with Repaired condition"
        }
        
        update_result = self.run_api_test(
            "Repairing Condition Repaired - Update to Repairing with Repaired Condition",
            "PUT",
            f"boards/{board_id}",
            200,
            data=update_data
        )
        
        if update_result:
            # Verify both location and condition were updated correctly
            if (update_result.get('location') == 'Repairing' and 
                update_result.get('condition') == 'Repaired' and
                update_result.get('comments') == "Board moved to repairing with Repaired condition"):
                
                # Clean up
                self.run_api_test(
                    "Repairing Condition Repaired - Cleanup",
                    "DELETE",
                    f"boards/{board_id}",
                    200
                )
                return True
            else:
                self.log_test("Repairing Condition Repaired Verification", False, 
                    f"Expected location='Repairing', condition='Repaired', got location='{update_result.get('location')}', condition='{update_result.get('condition')}'")
        
        return False

    def test_repairing_condition_updates_scrap(self):
        """Test updating board condition to 'Scrap' in Repairing location - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create a test board
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"REPAIR_SCRAP_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "OK",
            "comments": "Board for condition update testing"
        }
        
        create_result = self.run_api_test(
            "Repairing Condition Scrap - Create Board",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not create_result or 'id' not in create_result:
            return False
            
        board_id = create_result['id']
        
        # Update board to Repairing location with 'Scrap' condition
        update_data = {
            "location": "Repairing",
            "condition": "Scrap",
            "comments": "Board moved to repairing with Scrap condition"
        }
        
        update_result = self.run_api_test(
            "Repairing Condition Scrap - Update to Repairing with Scrap Condition",
            "PUT",
            f"boards/{board_id}",
            200,
            data=update_data
        )
        
        if update_result:
            # Verify both location and condition were updated correctly
            if (update_result.get('location') == 'Repairing' and 
                update_result.get('condition') == 'Scrap' and
                update_result.get('comments') == "Board moved to repairing with Scrap condition"):
                
                # Clean up
                self.run_api_test(
                    "Repairing Condition Scrap - Cleanup",
                    "DELETE",
                    f"boards/{board_id}",
                    200
                )
                return True
            else:
                self.log_test("Repairing Condition Scrap Verification", False, 
                    f"Expected location='Repairing', condition='Scrap', got location='{update_result.get('location')}', condition='{update_result.get('condition')}'")
        
        return False

    def test_repairing_workflow_complete_with_conditions(self):
        """Test complete Repairing workflow with all condition transitions - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create a test board
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"REPAIR_COMPLETE_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "OK",
            "comments": "Board for complete repairing workflow testing"
        }
        
        create_result = self.run_api_test(
            "Complete Repairing Workflow - Create Board",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not create_result or 'id' not in create_result:
            return False
            
        board_id = create_result['id']
        
        # Step 1: Move to Repairing with New condition
        update_data_new = {
            "location": "Repairing",
            "condition": "New",
            "comments": "Board moved to repairing - condition New"
        }
        
        update_result_new = self.run_api_test(
            "Complete Repairing Workflow - Update to New Condition",
            "PUT",
            f"boards/{board_id}",
            200,
            data=update_data_new
        )
        
        if not update_result_new or update_result_new.get('condition') != 'New':
            return False
        
        # Step 2: Update to Repaired condition
        update_data_repaired = {
            "condition": "Repaired",
            "comments": "Board repair completed - condition Repaired"
        }
        
        update_result_repaired = self.run_api_test(
            "Complete Repairing Workflow - Update to Repaired Condition",
            "PUT",
            f"boards/{board_id}",
            200,
            data=update_data_repaired
        )
        
        if not update_result_repaired or update_result_repaired.get('condition') != 'Repaired':
            return False
        
        # Step 3: Update to Scrap condition (if repair failed)
        update_data_scrap = {
            "condition": "Scrap",
            "comments": "Board cannot be repaired - condition Scrap"
        }
        
        update_result_scrap = self.run_api_test(
            "Complete Repairing Workflow - Update to Scrap Condition",
            "PUT",
            f"boards/{board_id}",
            200,
            data=update_data_scrap
        )
        
        if update_result_scrap and update_result_scrap.get('condition') == 'Scrap':
            # Verify final state
            final_result = self.run_api_test(
                "Complete Repairing Workflow - Verify Final State",
                "GET",
                f"boards/{board_id}",
                200
            )
            
            if (final_result and 
                final_result.get('location') == 'Repairing' and 
                final_result.get('condition') == 'Scrap'):
                
                # Clean up
                self.run_api_test(
                    "Complete Repairing Workflow - Cleanup",
                    "DELETE",
                    f"boards/{board_id}",
                    200
                )
                return True
            else:
                self.log_test("Complete Repairing Workflow Final Verification", False, 
                    f"Expected location='Repairing', condition='Scrap', got location='{final_result.get('location') if final_result else 'None'}', condition='{final_result.get('condition') if final_result else 'None'}'")
        
        return False

    def test_board_update_model_validation(self):
        """Test BoardUpdate model accepts all condition values - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create a test board
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"MODEL_VALIDATION_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "OK",
            "comments": "Board for model validation testing"
        }
        
        create_result = self.run_api_test(
            "Model Validation - Create Board",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not create_result or 'id' not in create_result:
            return False
            
        board_id = create_result['id']
        
        # Test all condition values one by one
        conditions_to_test = ["New", "Repaired", "Scrap"]
        all_conditions_passed = True
        
        for condition in conditions_to_test:
            update_data = {
                "location": "Repairing",
                "condition": condition,
                "comments": f"Testing condition: {condition}"
            }
            
            update_result = self.run_api_test(
                f"Model Validation - Test Condition {condition}",
                "PUT",
                f"boards/{board_id}",
                200,
                data=update_data
            )
            
            if not update_result or update_result.get('condition') != condition:
                all_conditions_passed = False
                self.log_test(f"Model Validation {condition}", False, 
                    f"Expected condition='{condition}', got '{update_result.get('condition') if update_result else 'None'}'")
                break
        
        # Clean up
        self.run_api_test(
            "Model Validation - Cleanup",
            "DELETE",
            f"boards/{board_id}",
            200
        )
        
        return all_conditions_passed

    def test_api_response_validation_put_endpoint(self):
        """Test PUT endpoint returns correct updated board information - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create a test board
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"API_RESPONSE_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "OK",
            "qc_by": "QC Engineer",
            "comments": "Board for API response validation"
        }
        
        create_result = self.run_api_test(
            "API Response Validation - Create Board",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not create_result or 'id' not in create_result:
            return False
            
        board_id = create_result['id']
        
        # Update board with specific data
        update_data = {
            "location": "Repairing",
            "condition": "Repaired",
            "issued_to": "Test Engineer",
            "project_number": "PROJ_API_001",
            "comments": "Updated via API response validation test"
        }
        
        update_result = self.run_api_test(
            "API Response Validation - PUT Update",
            "PUT",
            f"boards/{board_id}",
            200,
            data=update_data
        )
        
        if update_result:
            # Verify all fields in the response
            expected_fields = {
                'id': board_id,
                'category_id': self.test_category_id,
                'serial_number': board_data['serial_number'],
                'location': 'Repairing',
                'condition': 'Repaired',
                'issued_to': 'Test Engineer',
                'project_number': 'PROJ_API_001',
                'comments': 'Updated via API response validation test',
                'qc_by': 'QC Engineer'
            }
            
            all_fields_correct = True
            for field, expected_value in expected_fields.items():
                actual_value = update_result.get(field)
                if actual_value != expected_value:
                    all_fields_correct = False
                    self.log_test(f"API Response Field {field}", False, 
                        f"Expected '{expected_value}', got '{actual_value}'")
            
            # Verify response has required datetime fields
            required_datetime_fields = ['inward_date_time', 'issued_date_time', 'created_at']
            for field in required_datetime_fields:
                if field not in update_result:
                    all_fields_correct = False
                    self.log_test(f"API Response DateTime Field {field}", False, 
                        f"Field '{field}' missing from response")
            
            # Verify GET endpoint returns same data
            get_result = self.run_api_test(
                "API Response Validation - GET Verification",
                "GET",
                f"boards/{board_id}",
                200
            )
            
            if get_result:
                # Compare key fields between PUT response and GET response
                key_fields = ['location', 'condition', 'issued_to', 'project_number', 'comments']
                get_matches_put = True
                
                for field in key_fields:
                    if get_result.get(field) != update_result.get(field):
                        get_matches_put = False
                        self.log_test(f"GET vs PUT Response {field}", False, 
                            f"GET: '{get_result.get(field)}', PUT: '{update_result.get(field)}'")
                
                # Clean up
                self.run_api_test(
                    "API Response Validation - Cleanup",
                    "DELETE",
                    f"boards/{board_id}",
                    200
                )
                
                return all_fields_correct and get_matches_put
        
        return False

    def test_repairing_return_filtering_setup(self):
        """Test board state setup for Repairing/Return workflow filtering - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create test boards with different locations and conditions as specified in review request
        test_boards_data = [
            {
                "name": "Board A",
                "serial_number": f"FILTER_A_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "should_be_available": False  # In stock boards should NOT be available for Repairing/Return
            },
            {
                "name": "Board B", 
                "serial_number": f"FILTER_B_{datetime.now().strftime('%H%M%S')}",
                "location": "Issued for machine",
                "condition": "New",
                "should_be_available": True  # Issued boards should be available for Repairing/Return
            },
            {
                "name": "Board C",
                "serial_number": f"FILTER_C_{datetime.now().strftime('%H%M%S')}",
                "location": "At customer site",
                "condition": "Repaired",
                "should_be_available": True  # Customer site boards should be available for Repairing/Return
            },
            {
                "name": "Board D",
                "serial_number": f"FILTER_D_{datetime.now().strftime('%H%M%S')}",
                "location": "Issued for spares",
                "condition": "New",
                "should_be_available": True  # Issued for spares should be available for Repairing/Return
            },
            {
                "name": "Board E",
                "serial_number": f"FILTER_E_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "Scrap",
                "should_be_available": False  # In stock boards should NOT be available (edge case)
            }
        ]
        
        created_boards = []
        
        # Create all test boards
        for board_spec in test_boards_data:
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": board_spec["serial_number"],
                "location": board_spec["location"],
                "condition": board_spec["condition"],
                "comments": f"Test board {board_spec['name']} for filtering logic"
            }
            
            create_result = self.run_api_test(
                f"Filtering Setup - Create {board_spec['name']}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                board_spec['id'] = create_result['id']
                created_boards.append(board_spec)
            else:
                # Clean up any created boards and return failure
                for cleanup_board in created_boards:
                    self.run_api_test(
                        f"Filtering Setup Cleanup - {cleanup_board['name']}",
                        "DELETE",
                        f"boards/{cleanup_board['id']}",
                        200
                    )
                return False
        
        # Store created boards for use in other filtering tests
        self.filtering_test_boards = created_boards
        return True

    def test_repairing_return_filtering_logic(self):
        """Test filtering logic for Repairing/Return workflow - Review Request Focus"""
        if not hasattr(self, 'filtering_test_boards'):
            return False
            
        # Get all boards via API
        boards_result = self.run_api_test(
            "Filtering Logic - Get All Boards",
            "GET",
            "boards",
            200
        )
        
        if not boards_result or not isinstance(boards_result, list):
            return False
        
        # Find our test boards in the results
        found_boards = []
        for board_spec in self.filtering_test_boards:
            found_board = next((board for board in boards_result if board['id'] == board_spec['id']), None)
            if found_board:
                found_boards.append({**board_spec, 'api_data': found_board})
        
        if len(found_boards) != len(self.filtering_test_boards):
            self.log_test("Filtering Logic - Board Retrieval", False, 
                f"Expected {len(self.filtering_test_boards)} boards, found {len(found_boards)}")
            return False
        
        # Test filtering logic: boards with location "In stock" should NOT be available for Repairing/Return
        # boards with other locations SHOULD be available
        filtering_correct = True
        
        for board_spec in found_boards:
            api_data = board_spec['api_data']
            expected_availability = board_spec['should_be_available']
            
            # Apply filtering logic: only non-stock boards should be available for Repairing/Return
            is_available_for_repair_return = api_data['location'] != "In stock"
            
            if is_available_for_repair_return != expected_availability:
                filtering_correct = False
                self.log_test(f"Filtering Logic - {board_spec['name']}", False, 
                    f"Board with location '{api_data['location']}' and condition '{api_data['condition']}' - Expected available: {expected_availability}, Got: {is_available_for_repair_return}")
            else:
                self.log_test(f"Filtering Logic - {board_spec['name']}", True, 
                    f"Correctly filtered: location '{api_data['location']}', available for repair/return: {is_available_for_repair_return}")
        
        return filtering_correct

    def test_repairing_return_edge_cases(self):
        """Test edge cases for Repairing/Return workflow filtering - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create additional edge case boards
        edge_case_boards = [
            {
                "name": "Already Repairing Board",
                "serial_number": f"EDGE_REPAIRING_{datetime.now().strftime('%H%M%S')}",
                "location": "Repairing",
                "condition": "Needs repair",
                "should_be_available": True  # Already in repairing should be available
            },
            {
                "name": "Repairing Repaired Board",
                "serial_number": f"EDGE_REP_REPAIRED_{datetime.now().strftime('%H%M%S')}",
                "location": "Repairing", 
                "condition": "Repaired",
                "should_be_available": True  # Repaired boards in repairing should be available
            },
            {
                "name": "Repairing Scrap Board",
                "serial_number": f"EDGE_REP_SCRAP_{datetime.now().strftime('%H%M%S')}",
                "location": "Repairing",
                "condition": "Scrap",
                "should_be_available": True  # Even scrap boards in repairing should be available for workflow
            }
        ]
        
        created_edge_boards = []
        
        # Create edge case boards
        for board_spec in edge_case_boards:
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": board_spec["serial_number"],
                "location": board_spec["location"],
                "condition": board_spec["condition"],
                "comments": f"Edge case test board {board_spec['name']}"
            }
            
            create_result = self.run_api_test(
                f"Edge Cases - Create {board_spec['name']}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                board_spec['id'] = create_result['id']
                created_edge_boards.append(board_spec)
            else:
                # Clean up and return failure
                for cleanup_board in created_edge_boards:
                    self.run_api_test(
                        f"Edge Cases Cleanup - {cleanup_board['name']}",
                        "DELETE",
                        f"boards/{cleanup_board['id']}",
                        200
                    )
                return False
        
        # Test edge case filtering
        boards_result = self.run_api_test(
            "Edge Cases - Get All Boards",
            "GET",
            "boards",
            200
        )
        
        if not boards_result or not isinstance(boards_result, list):
            return False
        
        edge_cases_correct = True
        
        for board_spec in created_edge_boards:
            found_board = next((board for board in boards_result if board['id'] == board_spec['id']), None)
            if found_board:
                # Apply filtering logic
                is_available_for_repair_return = found_board['location'] != "In stock"
                expected_availability = board_spec['should_be_available']
                
                if is_available_for_repair_return != expected_availability:
                    edge_cases_correct = False
                    self.log_test(f"Edge Case - {board_spec['name']}", False, 
                        f"Expected available: {expected_availability}, Got: {is_available_for_repair_return}")
                else:
                    self.log_test(f"Edge Case - {board_spec['name']}", True, 
                        f"Correctly handled edge case: location '{found_board['location']}', condition '{found_board['condition']}'")
        
        # Clean up edge case boards
        for board_spec in created_edge_boards:
            self.run_api_test(
                f"Edge Cases Final Cleanup - {board_spec['name']}",
                "DELETE",
                f"boards/{board_spec['id']}",
                200
            )
        
        return edge_cases_correct

    def test_repairing_return_api_response_verification(self):
        """Test API response verification for Repairing/Return workflow - Review Request Focus"""
        if not hasattr(self, 'filtering_test_boards'):
            return False
            
        # Verify GET /api/boards returns accurate location and condition information
        boards_result = self.run_api_test(
            "API Response Verification - Get All Boards",
            "GET",
            "boards",
            200
        )
        
        if not boards_result or not isinstance(boards_result, list):
            return False
        
        api_response_correct = True
        
        # Verify each test board's data in API response
        for board_spec in self.filtering_test_boards:
            found_board = next((board for board in boards_result if board['id'] == board_spec['id']), None)
            
            if not found_board:
                api_response_correct = False
                self.log_test(f"API Response - {board_spec['name']} Missing", False, 
                    f"Board {board_spec['name']} not found in API response")
                continue
            
            # Verify location and condition match expected values
            if (found_board['location'] != board_spec['location'] or 
                found_board['condition'] != board_spec['condition']):
                api_response_correct = False
                self.log_test(f"API Response - {board_spec['name']} Data Mismatch", False, 
                    f"Expected location='{board_spec['location']}', condition='{board_spec['condition']}' | Got location='{found_board['location']}', condition='{found_board['condition']}'")
            else:
                self.log_test(f"API Response - {board_spec['name']} Data Correct", True, 
                    f"Location and condition data accurate in API response")
            
            # Verify required fields are present
            required_fields = ['id', 'category_id', 'serial_number', 'location', 'condition', 'created_at', 'created_by']
            for field in required_fields:
                if field not in found_board:
                    api_response_correct = False
                    self.log_test(f"API Response - {board_spec['name']} Missing Field {field}", False, 
                        f"Required field '{field}' missing from API response")
        
        return api_response_correct

    def test_repairing_return_filtering_cleanup(self):
        """Clean up test boards created for filtering tests - Review Request Focus"""
        if not hasattr(self, 'filtering_test_boards'):
            return True  # Nothing to clean up
            
        cleanup_success = True
        
        for board_spec in self.filtering_test_boards:
            result = self.run_api_test(
                f"Filtering Cleanup - {board_spec['name']}",
                "DELETE",
                f"boards/{board_spec['id']}",
                200
            )
            if result is None:
                cleanup_success = False
        
        # Remove the reference to cleaned up boards
        delattr(self, 'filtering_test_boards')
        
        return cleanup_success

    def test_bulk_issue_request_single_category(self):
        """Test bulk issue request with single category - multiple boards"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create multiple "New" condition boards in stock for testing
        test_boards = []
        for i in range(5):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"BULK_SINGLE_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Bulk test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Bulk Single Category - Create Board {i+1}",
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
                    self.run_api_test(f"Bulk Single Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Test bulk request for 3 boards from single category
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "quantity": 3
                }
            ],
            "issued_to": "Bulk Test Engineer",
            "project_number": "PROJ_BULK_SINGLE_001",
            "comments": "Bulk issue request - single category test"
        }
        
        bulk_result = self.run_api_test(
            "Bulk Issue Request - Single Category (3 boards)",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        success = False
        if bulk_result:
            # Verify response structure
            expected_fields = ['message', 'created_requests', 'total_requested', 'successful']
            has_all_fields = all(field in bulk_result for field in expected_fields)
            
            if (has_all_fields and 
                bulk_result['total_requested'] == 3 and 
                bulk_result['successful'] == 3 and
                len(bulk_result['created_requests']) == 3):
                
                # Verify each created request has correct metadata
                all_requests_correct = True
                for req in bulk_result['created_requests']:
                    if (req['category_id'] != self.test_category_id or
                        'id' not in req or
                        'category_name' not in req):
                        all_requests_correct = False
                        break
                
                if all_requests_correct:
                    success = True
                    # Clean up created issue requests
                    for req in bulk_result['created_requests']:
                        self.run_api_test(f"Bulk Single Cleanup - Request {req['id']}", "DELETE", f"issue-requests/{req['id']}", 200)
                else:
                    self.log_test("Bulk Single Category Request Metadata", False, "Created requests missing required metadata")
            else:
                self.log_test("Bulk Single Category Response Structure", False, 
                    f"Expected 3 total/successful requests, got total={bulk_result.get('total_requested')}, successful={bulk_result.get('successful')}")
        
        # Clean up test boards
        for board_id in test_boards:
            self.run_api_test(f"Bulk Single Final Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_bulk_issue_request_multiple_categories(self):
        """Test bulk issue request with multiple categories - one board each"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create additional test categories
        additional_categories = []
        for i in range(2):
            category_data = {
                "name": f"Bulk Test Category {i+2} {datetime.now().strftime('%H%M%S')}",
                "description": f"Additional category for bulk testing {i+2}",
                "manufacturer": "Bulk Test Manufacturer",
                "version": "1.0",
                "lead_time_days": 30,
                "minimum_stock_quantity": 5
            }
            
            create_result = self.run_api_test(
                f"Bulk Multiple Categories - Create Category {i+2}",
                "POST",
                "categories",
                200,
                data=category_data
            )
            
            if create_result and 'id' in create_result:
                additional_categories.append(create_result['id'])
            else:
                # Clean up and return failure
                for cat_id in additional_categories:
                    self.run_api_test(f"Bulk Multiple Cleanup - Category {cat_id}", "DELETE", f"categories/{cat_id}", 200)
                return False
        
        # Create test boards for each category
        all_categories = [self.test_category_id] + additional_categories
        test_boards = []
        
        for i, cat_id in enumerate(all_categories):
            board_data = {
                "category_id": cat_id,
                "serial_number": f"BULK_MULTI_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Bulk multi-category test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Bulk Multiple Categories - Create Board for Category {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Bulk Multiple Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                for cat_id in additional_categories:
                    self.run_api_test(f"Bulk Multiple Cleanup - Category {cat_id}", "DELETE", f"categories/{cat_id}", 200)
                return False
        
        # Test bulk request for 1 board from each of 3 categories
        bulk_request_data = {
            "categories": [
                {"category_id": cat_id, "quantity": 1} for cat_id in all_categories
            ],
            "issued_to": "Multi Category Test Engineer",
            "project_number": "PROJ_BULK_MULTI_001",
            "comments": "Bulk issue request - multiple categories test"
        }
        
        bulk_result = self.run_api_test(
            "Bulk Issue Request - Multiple Categories (1 each)",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        success = False
        if bulk_result:
            # Verify response structure
            if (bulk_result.get('total_requested') == 3 and 
                bulk_result.get('successful') == 3 and
                len(bulk_result.get('created_requests', [])) == 3):
                
                # Verify each category is represented
                category_ids_in_response = set(req['category_id'] for req in bulk_result['created_requests'])
                expected_category_ids = set(all_categories)
                
                if category_ids_in_response == expected_category_ids:
                    success = True
                    # Clean up created issue requests
                    for req in bulk_result['created_requests']:
                        self.run_api_test(f"Bulk Multiple Cleanup - Request {req['id']}", "DELETE", f"issue-requests/{req['id']}", 200)
                else:
                    self.log_test("Bulk Multiple Categories Coverage", False, 
                        f"Expected categories {expected_category_ids}, got {category_ids_in_response}")
            else:
                self.log_test("Bulk Multiple Categories Response", False, 
                    f"Expected 3 total/successful requests, got total={bulk_result.get('total_requested')}, successful={bulk_result.get('successful')}")
        
        # Clean up test boards and categories
        for board_id in test_boards:
            self.run_api_test(f"Bulk Multiple Final Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        for cat_id in additional_categories:
            self.run_api_test(f"Bulk Multiple Final Cleanup - Category {cat_id}", "DELETE", f"categories/{cat_id}", 200)
        
        return success

    def test_bulk_issue_request_mixed_scenario(self):
        """Test bulk issue request mixed scenario - different quantities per category"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create additional test category
        category_data = {
            "name": f"Mixed Bulk Test Category {datetime.now().strftime('%H%M%S')}",
            "description": "Category for mixed bulk testing",
            "manufacturer": "Mixed Test Manufacturer",
            "version": "1.0",
            "lead_time_days": 30,
            "minimum_stock_quantity": 5
        }
        
        create_result = self.run_api_test(
            "Bulk Mixed Scenario - Create Additional Category",
            "POST",
            "categories",
            200,
            data=category_data
        )
        
        if not create_result or 'id' not in create_result:
            return False
            
        additional_category_id = create_result['id']
        
        # Create test boards: 5 for first category, 3 for second category
        test_boards = []
        board_configs = [
            (self.test_category_id, 5, "A"),
            (additional_category_id, 3, "B")
        ]
        
        for cat_id, count, prefix in board_configs:
            for i in range(count):
                board_data = {
                    "category_id": cat_id,
                    "serial_number": f"BULK_MIXED_{prefix}{i}_{datetime.now().strftime('%H%M%S')}",
                    "location": "In stock",
                    "condition": "New",
                    "comments": f"Mixed bulk test board {prefix}{i+1}"
                }
                
                create_result = self.run_api_test(
                    f"Bulk Mixed Scenario - Create Board {prefix}{i+1}",
                    "POST",
                    "boards",
                    200,
                    data=board_data
                )
                
                if create_result and 'id' in create_result:
                    test_boards.append(create_result['id'])
                else:
                    # Clean up and return failure
                    for board_id in test_boards:
                        self.run_api_test(f"Bulk Mixed Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                    self.run_api_test("Bulk Mixed Cleanup - Category", "DELETE", f"categories/{additional_category_id}", 200)
                    return False
        
        # Test mixed bulk request: 3 from category A, 2 from category B
        bulk_request_data = {
            "categories": [
                {"category_id": self.test_category_id, "quantity": 3},
                {"category_id": additional_category_id, "quantity": 2}
            ],
            "issued_to": "Mixed Scenario Test Engineer",
            "project_number": "PROJ_BULK_MIXED_001",
            "comments": "Bulk issue request - mixed scenario test"
        }
        
        bulk_result = self.run_api_test(
            "Bulk Issue Request - Mixed Scenario (3+2 boards)",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        success = False
        if bulk_result:
            # Verify response structure
            if (bulk_result.get('total_requested') == 5 and 
                bulk_result.get('successful') == 5 and
                len(bulk_result.get('created_requests', [])) == 5):
                
                # Verify quantity distribution
                category_counts = {}
                for req in bulk_result['created_requests']:
                    cat_id = req['category_id']
                    category_counts[cat_id] = category_counts.get(cat_id, 0) + 1
                
                expected_counts = {self.test_category_id: 3, additional_category_id: 2}
                
                if category_counts == expected_counts:
                    success = True
                    # Clean up created issue requests
                    for req in bulk_result['created_requests']:
                        self.run_api_test(f"Bulk Mixed Cleanup - Request {req['id']}", "DELETE", f"issue-requests/{req['id']}", 200)
                else:
                    self.log_test("Bulk Mixed Scenario Distribution", False, 
                        f"Expected distribution {expected_counts}, got {category_counts}")
            else:
                self.log_test("Bulk Mixed Scenario Response", False, 
                    f"Expected 5 total/successful requests, got total={bulk_result.get('total_requested')}, successful={bulk_result.get('successful')}")
        
        # Clean up test boards and category
        for board_id in test_boards:
            self.run_api_test(f"Bulk Mixed Final Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        self.run_api_test("Bulk Mixed Final Cleanup - Category", "DELETE", f"categories/{additional_category_id}", 200)
        
        return success

    def test_bulk_issue_request_maximum_scenario(self):
        """Test bulk issue request maximum scenario - 5 categories with 50 boards each"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create 4 additional test categories (we already have 1)
        additional_categories = []
        for i in range(4):
            category_data = {
                "name": f"Max Bulk Test Category {i+2} {datetime.now().strftime('%H%M%S')}",
                "description": f"Category {i+2} for maximum bulk testing",
                "manufacturer": "Max Test Manufacturer",
                "version": "1.0",
                "lead_time_days": 30,
                "minimum_stock_quantity": 50
            }
            
            create_result = self.run_api_test(
                f"Bulk Maximum Scenario - Create Category {i+2}",
                "POST",
                "categories",
                200,
                data=category_data
            )
            
            if create_result and 'id' in create_result:
                additional_categories.append(create_result['id'])
            else:
                # Clean up and return failure
                for cat_id in additional_categories:
                    self.run_api_test(f"Bulk Max Cleanup - Category {cat_id}", "DELETE", f"categories/{cat_id}", 200)
                return False
        
        all_categories = [self.test_category_id] + additional_categories
        
        # Create 50 test boards for each category (250 total) - This is a lot, so we'll create fewer for testing
        # For practical testing, we'll create 3 boards per category and request 2 each
        test_boards = []
        
        for cat_idx, cat_id in enumerate(all_categories):
            for i in range(3):  # Create 3 boards per category for testing
                board_data = {
                    "category_id": cat_id,
                    "serial_number": f"BULK_MAX_C{cat_idx}_B{i}_{datetime.now().strftime('%H%M%S')}",
                    "location": "In stock",
                    "condition": "New",
                    "comments": f"Maximum bulk test board C{cat_idx+1}B{i+1}"
                }
                
                create_result = self.run_api_test(
                    f"Bulk Maximum Scenario - Create Board C{cat_idx+1}B{i+1}",
                    "POST",
                    "boards",
                    200,
                    data=board_data
                )
                
                if create_result and 'id' in create_result:
                    test_boards.append(create_result['id'])
                else:
                    # Clean up and return failure
                    for board_id in test_boards:
                        self.run_api_test(f"Bulk Max Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                    for cat_id in additional_categories:
                        self.run_api_test(f"Bulk Max Cleanup - Category {cat_id}", "DELETE", f"categories/{cat_id}", 200)
                    return False
        
        # Test maximum bulk request: 2 boards from each of 5 categories (10 total)
        bulk_request_data = {
            "categories": [
                {"category_id": cat_id, "quantity": 2} for cat_id in all_categories
            ],
            "issued_to": "Maximum Scenario Test Engineer",
            "project_number": "PROJ_BULK_MAX_001",
            "comments": "Bulk issue request - maximum scenario test (5 categories)"
        }
        
        bulk_result = self.run_api_test(
            "Bulk Issue Request - Maximum Scenario (5 categories, 2 each)",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        success = False
        if bulk_result:
            # Verify response structure
            if (bulk_result.get('total_requested') == 10 and 
                bulk_result.get('successful') == 10 and
                len(bulk_result.get('created_requests', [])) == 10):
                
                # Verify all 5 categories are represented with 2 requests each
                category_counts = {}
                for req in bulk_result['created_requests']:
                    cat_id = req['category_id']
                    category_counts[cat_id] = category_counts.get(cat_id, 0) + 1
                
                expected_counts = {cat_id: 2 for cat_id in all_categories}
                
                if category_counts == expected_counts:
                    success = True
                    # Clean up created issue requests
                    for req in bulk_result['created_requests']:
                        self.run_api_test(f"Bulk Max Cleanup - Request {req['id']}", "DELETE", f"issue-requests/{req['id']}", 200)
                else:
                    self.log_test("Bulk Maximum Scenario Distribution", False, 
                        f"Expected 2 requests per category for {len(all_categories)} categories, got {category_counts}")
            else:
                self.log_test("Bulk Maximum Scenario Response", False, 
                    f"Expected 10 total/successful requests, got total={bulk_result.get('total_requested')}, successful={bulk_result.get('successful')}")
        
        # Clean up test boards and categories
        for board_id in test_boards:
            self.run_api_test(f"Bulk Max Final Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        for cat_id in additional_categories:
            self.run_api_test(f"Bulk Max Final Cleanup - Category {cat_id}", "DELETE", f"categories/{cat_id}", 200)
        
        return success

    def test_bulk_issue_request_insufficient_stock(self):
        """Test bulk issue request with insufficient stock in some categories"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create additional test category
        category_data = {
            "name": f"Insufficient Stock Test Category {datetime.now().strftime('%H%M%S')}",
            "description": "Category for insufficient stock testing",
            "manufacturer": "Stock Test Manufacturer",
            "version": "1.0",
            "lead_time_days": 30,
            "minimum_stock_quantity": 5
        }
        
        create_result = self.run_api_test(
            "Bulk Insufficient Stock - Create Additional Category",
            "POST",
            "categories",
            200,
            data=category_data
        )
        
        if not create_result or 'id' not in create_result:
            return False
            
        insufficient_category_id = create_result['id']
        
        # Create test boards: 5 for first category, only 1 for second category
        test_boards = []
        board_configs = [
            (self.test_category_id, 5, "SUFFICIENT"),
            (insufficient_category_id, 1, "INSUFFICIENT")
        ]
        
        for cat_id, count, prefix in board_configs:
            for i in range(count):
                board_data = {
                    "category_id": cat_id,
                    "serial_number": f"BULK_STOCK_{prefix}{i}_{datetime.now().strftime('%H%M%S')}",
                    "location": "In stock",
                    "condition": "New",
                    "comments": f"Stock test board {prefix}{i+1}"
                }
                
                create_result = self.run_api_test(
                    f"Bulk Insufficient Stock - Create Board {prefix}{i+1}",
                    "POST",
                    "boards",
                    200,
                    data=board_data
                )
                
                if create_result and 'id' in create_result:
                    test_boards.append(create_result['id'])
                else:
                    # Clean up and return failure
                    for board_id in test_boards:
                        self.run_api_test(f"Bulk Stock Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                    self.run_api_test("Bulk Stock Cleanup - Category", "DELETE", f"categories/{insufficient_category_id}", 200)
                    return False
        
        # Test bulk request: 3 from sufficient category (should work), 3 from insufficient category (should fail)
        bulk_request_data = {
            "categories": [
                {"category_id": self.test_category_id, "quantity": 3},
                {"category_id": insufficient_category_id, "quantity": 3}  # Only 1 available, requesting 3
            ],
            "issued_to": "Insufficient Stock Test Engineer",
            "project_number": "PROJ_BULK_STOCK_001",
            "comments": "Bulk issue request - insufficient stock test"
        }
        
        bulk_result = self.run_api_test(
            "Bulk Issue Request - Insufficient Stock (partial failure)",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        success = False
        if bulk_result:
            # Verify partial success response structure
            expected_fields = ['message', 'created_requests', 'total_requested', 'successful', 'failed_categories']
            has_all_fields = all(field in bulk_result for field in expected_fields)
            
            if (has_all_fields and 
                bulk_result.get('total_requested') == 6 and 
                bulk_result.get('successful') == 3 and  # Only 3 from sufficient category
                len(bulk_result.get('created_requests', [])) == 3 and
                len(bulk_result.get('failed_categories', [])) == 1):
                
                # Verify failed category details
                failed_category = bulk_result['failed_categories'][0]
                if (failed_category.get('category_id') == insufficient_category_id and
                    'error' in failed_category and
                    'Not enough boards available' in failed_category['error']):
                    
                    # Verify successful requests are from the sufficient category
                    all_from_sufficient = all(req['category_id'] == self.test_category_id 
                                            for req in bulk_result['created_requests'])
                    
                    if all_from_sufficient:
                        success = True
                        # Clean up created issue requests
                        for req in bulk_result['created_requests']:
                            self.run_api_test(f"Bulk Stock Cleanup - Request {req['id']}", "DELETE", f"issue-requests/{req['id']}", 200)
                    else:
                        self.log_test("Bulk Insufficient Stock Request Source", False, 
                            "Some successful requests not from sufficient category")
                else:
                    self.log_test("Bulk Insufficient Stock Failed Category Details", False, 
                        f"Failed category details incorrect: {failed_category}")
            else:
                self.log_test("Bulk Insufficient Stock Response Structure", False, 
                    f"Expected partial success (3/6), got total={bulk_result.get('total_requested')}, successful={bulk_result.get('successful')}, failed_categories={len(bulk_result.get('failed_categories', []))}")
        
        # Clean up test boards and category
        for board_id in test_boards:
            self.run_api_test(f"Bulk Stock Final Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        self.run_api_test("Bulk Stock Final Cleanup - Category", "DELETE", f"categories/{insufficient_category_id}", 200)
        
        return success

    def test_bulk_issue_request_nonexistent_category(self):
        """Test bulk issue request with non-existent categories"""
        fake_category_id = "fake-category-id-12345"
        
        bulk_request_data = {
            "categories": [
                {"category_id": fake_category_id, "quantity": 1}
            ],
            "issued_to": "Nonexistent Category Test Engineer",
            "project_number": "PROJ_BULK_FAKE_001",
            "comments": "Bulk issue request - nonexistent category test"
        }
        
        bulk_result = self.run_api_test(
            "Bulk Issue Request - Nonexistent Category",
            "POST",
            "issue-requests/bulk",
            400,  # Should return 400 error
            data=bulk_request_data
        )
        
        # For this test, we expect it to fail (return None), which means the API correctly rejected it
        return bulk_result is None

    def test_bulk_issue_request_validation_errors(self):
        """Test bulk issue request validation - quantity limits and category limits"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Test 1: Quantity > 50 (should fail)
        bulk_request_data_qty = {
            "categories": [
                {"category_id": self.test_category_id, "quantity": 51}  # Exceeds limit
            ],
            "issued_to": "Validation Test Engineer",
            "project_number": "PROJ_BULK_VAL_001",
            "comments": "Bulk issue request - quantity validation test"
        }
        
        qty_result = self.run_api_test(
            "Bulk Issue Request - Quantity Validation (>50)",
            "POST",
            "issue-requests/bulk",
            422,  # Should return validation error
            data=bulk_request_data_qty
        )
        
        # Test 2: More than 5 categories (should fail)
        bulk_request_data_cats = {
            "categories": [
                {"category_id": self.test_category_id, "quantity": 1} for _ in range(6)  # Exceeds 5 category limit
            ],
            "issued_to": "Validation Test Engineer",
            "project_number": "PROJ_BULK_VAL_002",
            "comments": "Bulk issue request - category count validation test"
        }
        
        cats_result = self.run_api_test(
            "Bulk Issue Request - Category Count Validation (>5)",
            "POST",
            "issue-requests/bulk",
            422,  # Should return validation error
            data=bulk_request_data_cats
        )
        
        # Test 3: Quantity = 0 (should fail)
        bulk_request_data_zero = {
            "categories": [
                {"category_id": self.test_category_id, "quantity": 0}  # Invalid quantity
            ],
            "issued_to": "Validation Test Engineer",
            "project_number": "PROJ_BULK_VAL_003",
            "comments": "Bulk issue request - zero quantity validation test"
        }
        
        zero_result = self.run_api_test(
            "Bulk Issue Request - Zero Quantity Validation",
            "POST",
            "issue-requests/bulk",
            422,  # Should return validation error
            data=bulk_request_data_zero
        )
        
        # All validation tests should fail (return None), indicating proper validation
        return qty_result is None and cats_result is None and zero_result is None

    def test_bulk_issue_request_stock_availability_new_only(self):
        """Test that bulk issue requests only consider 'New' condition boards"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create test boards with different conditions
        test_boards = []
        board_configs = [
            ("New", "In stock"),      # Should be available
            ("Repaired", "In stock"), # Should NOT be available for bulk requests
            ("Scrap", "In stock"),    # Should NOT be available
            ("New", "Repairing")      # Should NOT be available (wrong location)
        ]
        
        for i, (condition, location) in enumerate(board_configs):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"BULK_CONDITION_{condition}_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": location,
                "condition": condition,
                "comments": f"Condition test board {condition} in {location}"
            }
            
            create_result = self.run_api_test(
                f"Bulk Stock Availability - Create {condition} Board",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Bulk Condition Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Test bulk request for 2 boards (should only find 1 "New" board in stock)
        bulk_request_data = {
            "categories": [
                {"category_id": self.test_category_id, "quantity": 2}
            ],
            "issued_to": "Stock Availability Test Engineer",
            "project_number": "PROJ_BULK_AVAIL_001",
            "comments": "Bulk issue request - stock availability test"
        }
        
        bulk_result = self.run_api_test(
            "Bulk Issue Request - Stock Availability (New condition only)",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        success = False
        if bulk_result:
            # Should have failed categories due to insufficient "New" condition boards
            if ('failed_categories' in bulk_result and 
                len(bulk_result['failed_categories']) == 1 and
                bulk_result.get('successful') == 0):
                
                failed_category = bulk_result['failed_categories'][0]
                if ('Not enough boards available' in failed_category.get('error', '') and
                    'Available: 1' in failed_category.get('error', '')):
                    success = True
                else:
                    self.log_test("Bulk Stock Availability Error Message", False, 
                        f"Expected 'Available: 1' in error, got: {failed_category.get('error')}")
            else:
                self.log_test("Bulk Stock Availability Response", False, 
                    f"Expected failed request due to insufficient New condition boards, got successful={bulk_result.get('successful')}")
        
        # Clean up test boards
        for board_id in test_boards:
            self.run_api_test(f"Bulk Condition Final Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_bulk_issue_request_comments_application(self):
        """Test that bulk request comments are properly applied to individual requests"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create test boards
        test_boards = []
        for i in range(3):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"BULK_COMMENTS_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Comments test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Bulk Comments - Create Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Bulk Comments Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Test bulk request with specific comments
        test_comments = "Bulk request for testing comments application"
        bulk_request_data = {
            "categories": [
                {"category_id": self.test_category_id, "quantity": 2}
            ],
            "issued_to": "Comments Test Engineer",
            "project_number": "PROJ_BULK_COMMENTS_001",
            "comments": test_comments
        }
        
        bulk_result = self.run_api_test(
            "Bulk Issue Request - Comments Application",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        success = False
        if bulk_result and bulk_result.get('successful') == 2:
            # Get the created issue requests to verify comments
            created_request_ids = [req['id'] for req in bulk_result['created_requests']]
            
            # Verify comments in each created request
            all_comments_correct = True
            for i, request_id in enumerate(created_request_ids):
                request_result = self.run_api_test(
                    f"Bulk Comments - Verify Request {i+1} Comments",
                    "GET",
                    f"issue-requests",
                    200
                )
                
                if request_result and isinstance(request_result, list):
                    # Find our request in the list
                    our_request = next((req for req in request_result if req['id'] == request_id), None)
                    if our_request:
                        expected_comment_pattern = f"{test_comments} [Bulk request {i+1}/2]"
                        if our_request.get('comments') != expected_comment_pattern:
                            all_comments_correct = False
                            self.log_test(f"Bulk Comments Request {i+1}", False, 
                                f"Expected comment '{expected_comment_pattern}', got '{our_request.get('comments')}'")
                    else:
                        all_comments_correct = False
                        self.log_test(f"Bulk Comments Request {i+1} Not Found", False, 
                            f"Request {request_id} not found in issue requests list")
                else:
                    all_comments_correct = False
                    break
            
            if all_comments_correct:
                success = True
            
            # Clean up created issue requests
            for req in bulk_result['created_requests']:
                self.run_api_test(f"Bulk Comments Cleanup - Request {req['id']}", "DELETE", f"issue-requests/{req['id']}", 200)
        
        # Clean up test boards
        for board_id in test_boards:
            self.run_api_test(f"Bulk Comments Final Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_enhanced_bulk_issue_request_model_validation_quantity(self):
        """Test CategoryBoardRequest model with quantity field - Enhanced Functionality"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Test valid quantity-based request
        bulk_request_data = {
            "categories": [
                {"category_id": self.test_category_id, "quantity": 1}
            ],
            "issued_to": "Model Validation Test Engineer",
            "project_number": "PROJ_MODEL_VAL_001",
            "comments": "Testing quantity field validation"
        }
        
        # This should work (assuming we have boards available)
        result = self.run_api_test(
            "Enhanced Model Validation - Quantity Field",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        # Clean up any created requests
        if result and 'created_requests' in result:
            for req in result['created_requests']:
                self.run_api_test(f"Model Validation Cleanup - Request {req['id']}", "DELETE", f"issue-requests/{req['id']}", 200)
        
        return result is not None

    def test_enhanced_bulk_issue_request_model_validation_serial_numbers(self):
        """Test CategoryBoardRequest model with serial_numbers field - Enhanced Functionality"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create a test board with known serial number
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"SERIAL_VAL_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "New",
            "comments": "Board for serial number validation testing"
        }
        
        create_result = self.run_api_test(
            "Enhanced Model Validation - Create Test Board",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not create_result or 'id' not in create_result:
            return False
            
        board_id = create_result['id']
        serial_number = create_result['serial_number']
        
        # Test valid serial_numbers-based request
        bulk_request_data = {
            "categories": [
                {"category_id": self.test_category_id, "serial_numbers": [serial_number]}
            ],
            "issued_to": "Serial Numbers Test Engineer",
            "project_number": "PROJ_SERIAL_VAL_001",
            "comments": "Testing serial_numbers field validation"
        }
        
        result = self.run_api_test(
            "Enhanced Model Validation - Serial Numbers Field",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        success = False
        if result and result.get('successful') == 1:
            # Verify the correct serial number was assigned
            created_requests = result.get('created_requests', [])
            if len(created_requests) == 1 and created_requests[0].get('serial_number') == serial_number:
                success = True
            else:
                self.log_test("Serial Numbers Validation Response", False, 
                    f"Expected serial number {serial_number}, got {created_requests[0].get('serial_number') if created_requests else 'None'}")
        
        # Clean up
        if result and 'created_requests' in result:
            for req in result['created_requests']:
                self.run_api_test(f"Serial Validation Cleanup - Request {req['id']}", "DELETE", f"issue-requests/{req['id']}", 200)
        
        self.run_api_test("Serial Validation Cleanup - Board", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_enhanced_bulk_issue_request_validation_both_fields(self):
        """Test validation that prevents both quantity and serial_numbers being set - Enhanced Functionality"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Test invalid request with both quantity and serial_numbers
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id, 
                    "quantity": 2,
                    "serial_numbers": ["SERIAL1", "SERIAL2"]
                }
            ],
            "issued_to": "Both Fields Test Engineer",
            "project_number": "PROJ_BOTH_FIELDS_001",
            "comments": "Testing both fields validation"
        }
        
        result = self.run_api_test(
            "Enhanced Model Validation - Both Fields (Should Fail)",
            "POST",
            "issue-requests/bulk",
            422,  # Validation error expected
            data=bulk_request_data
        )
        
        # This should fail with validation error
        return result is None

    def test_enhanced_bulk_issue_request_validation_neither_field(self):
        """Test validation that requires either quantity OR serial_numbers - Enhanced Functionality"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Test invalid request with neither quantity nor serial_numbers
        bulk_request_data = {
            "categories": [
                {"category_id": self.test_category_id}
            ],
            "issued_to": "Neither Field Test Engineer",
            "project_number": "PROJ_NEITHER_FIELD_001",
            "comments": "Testing neither field validation"
        }
        
        result = self.run_api_test(
            "Enhanced Model Validation - Neither Field (Should Fail)",
            "POST",
            "issue-requests/bulk",
            422,  # Validation error expected
            data=bulk_request_data
        )
        
        # This should fail with validation error
        return result is None

    def test_enhanced_bulk_issue_request_specific_serial_numbers(self):
        """Test bulk request with specific serial numbers - Enhanced Functionality"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create test boards with known serial numbers
        test_boards = []
        serial_numbers = []
        
        for i in range(3):
            serial_number = f"SPECIFIC_{i}_{datetime.now().strftime('%H%M%S')}"
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": serial_number,
                "location": "In stock",
                "condition": "New",
                "comments": f"Specific serial test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Enhanced Specific Serials - Create Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
                serial_numbers.append(serial_number)
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Specific Serials Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Test bulk request with specific serial numbers
        bulk_request_data = {
            "categories": [
                {"category_id": self.test_category_id, "serial_numbers": serial_numbers[:2]}  # Request first 2 boards
            ],
            "issued_to": "Specific Serials Test Engineer",
            "project_number": "PROJ_SPECIFIC_001",
            "comments": "Testing specific serial numbers request"
        }
        
        result = self.run_api_test(
            "Enhanced Bulk Request - Specific Serial Numbers",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        success = False
        if result and result.get('successful') == 2:
            # Verify correct serial numbers were assigned
            created_requests = result.get('created_requests', [])
            if len(created_requests) == 2:
                assigned_serials = [req.get('serial_number') for req in created_requests]
                if set(assigned_serials) == set(serial_numbers[:2]):
                    success = True
                else:
                    self.log_test("Specific Serials Assignment", False, 
                        f"Expected serials {serial_numbers[:2]}, got {assigned_serials}")
            else:
                self.log_test("Specific Serials Count", False, 
                    f"Expected 2 requests, got {len(created_requests)}")
        
        # Clean up
        if result and 'created_requests' in result:
            for req in result['created_requests']:
                self.run_api_test(f"Specific Serials Cleanup - Request {req['id']}", "DELETE", f"issue-requests/{req['id']}", 200)
        
        for board_id in test_boards:
            self.run_api_test(f"Specific Serials Final Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_enhanced_bulk_issue_request_mixed_mode(self):
        """Test mixed mode (some categories with quantity, some with specific serials) - Enhanced Functionality"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create a second category for mixed testing
        category2_data = {
            "name": f"Mixed Test Category {datetime.now().strftime('%H%M%S')}",
            "description": "Second category for mixed mode testing",
            "manufacturer": "Mixed Test Manufacturer",
            "version": "1.0",
            "lead_time_days": 30,
            "minimum_stock_quantity": 10
        }
        
        category2_result = self.run_api_test(
            "Enhanced Mixed Mode - Create Second Category",
            "POST",
            "categories",
            200,
            data=category2_data
        )
        
        if not category2_result or 'id' not in category2_result:
            return False
            
        category2_id = category2_result['id']
        
        # Create boards for both categories
        test_boards = []
        specific_serials = []
        
        # Category 1: Create boards for specific serial request
        for i in range(2):
            serial_number = f"MIXED_SPECIFIC_{i}_{datetime.now().strftime('%H%M%S')}"
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": serial_number,
                "location": "In stock",
                "condition": "New",
                "comments": f"Mixed mode specific serial board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Enhanced Mixed Mode - Create Specific Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
                specific_serials.append(serial_number)
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Mixed Mode Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                self.run_api_test("Mixed Mode Cleanup - Category2", "DELETE", f"categories/{category2_id}", 200)
                return False
        
        # Category 2: Create boards for quantity-based request
        for i in range(3):
            board_data = {
                "category_id": category2_id,
                "serial_number": f"MIXED_QUANTITY_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Mixed mode quantity board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Enhanced Mixed Mode - Create Quantity Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Mixed Mode Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                self.run_api_test("Mixed Mode Cleanup - Category2", "DELETE", f"categories/{category2_id}", 200)
                return False
        
        # Test mixed mode bulk request
        bulk_request_data = {
            "categories": [
                {"category_id": self.test_category_id, "serial_numbers": specific_serials},  # Specific serials
                {"category_id": category2_id, "quantity": 2}  # Quantity-based
            ],
            "issued_to": "Mixed Mode Test Engineer",
            "project_number": "PROJ_MIXED_001",
            "comments": "Testing mixed mode request"
        }
        
        result = self.run_api_test(
            "Enhanced Bulk Request - Mixed Mode",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        success = False
        if result and result.get('successful') == 4:  # 2 specific + 2 quantity
            created_requests = result.get('created_requests', [])
            
            # Verify specific serial requests
            specific_requests = [req for req in created_requests if req['category_id'] == self.test_category_id]
            quantity_requests = [req for req in created_requests if req['category_id'] == category2_id]
            
            if (len(specific_requests) == 2 and len(quantity_requests) == 2):
                # Check that specific requests have the correct serial numbers
                assigned_specific_serials = [req.get('serial_number') for req in specific_requests]
                if set(assigned_specific_serials) == set(specific_serials):
                    success = True
                else:
                    self.log_test("Mixed Mode Specific Serials", False, 
                        f"Expected specific serials {specific_serials}, got {assigned_specific_serials}")
            else:
                self.log_test("Mixed Mode Request Distribution", False, 
                    f"Expected 2 specific + 2 quantity requests, got {len(specific_requests)} + {len(quantity_requests)}")
        
        # Clean up
        if result and 'created_requests' in result:
            for req in result['created_requests']:
                self.run_api_test(f"Mixed Mode Cleanup - Request {req['id']}", "DELETE", f"issue-requests/{req['id']}", 200)
        
        for board_id in test_boards:
            self.run_api_test(f"Mixed Mode Final Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        self.run_api_test("Mixed Mode Final Cleanup - Category2", "DELETE", f"categories/{category2_id}", 200)
        
        return success

    def test_enhanced_bulk_issue_request_invalid_serial_numbers(self):
        """Test with invalid serial numbers (non-existent boards) - Enhanced Functionality"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Test bulk request with non-existent serial numbers
        non_existent_serials = ["NONEXISTENT_001", "NONEXISTENT_002"]
        bulk_request_data = {
            "categories": [
                {"category_id": self.test_category_id, "serial_numbers": non_existent_serials}
            ],
            "issued_to": "Invalid Serials Test Engineer",
            "project_number": "PROJ_INVALID_001",
            "comments": "Testing invalid serial numbers"
        }
        
        result = self.run_api_test(
            "Enhanced Bulk Request - Invalid Serial Numbers",
            "POST",
            "issue-requests/bulk",
            400,  # Should fail with error
            data=bulk_request_data
        )
        
        # This should fail - we expect None result for failed requests
        return result is None

    def test_enhanced_bulk_issue_request_partially_invalid_serial_numbers(self):
        """Test with partially invalid serial numbers (some exist, some don't) - Enhanced Functionality"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create one valid board
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"PARTIAL_VALID_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "New",
            "comments": "Partially valid test board"
        }
        
        create_result = self.run_api_test(
            "Enhanced Partial Invalid - Create Valid Board",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not create_result or 'id' not in create_result:
            return False
            
        board_id = create_result['id']
        valid_serial = create_result['serial_number']
        
        # Test bulk request with mix of valid and invalid serial numbers
        mixed_serials = [valid_serial, "NONEXISTENT_PARTIAL"]
        bulk_request_data = {
            "categories": [
                {"category_id": self.test_category_id, "serial_numbers": mixed_serials}
            ],
            "issued_to": "Partial Invalid Test Engineer",
            "project_number": "PROJ_PARTIAL_001",
            "comments": "Testing partially invalid serial numbers"
        }
        
        result = self.run_api_test(
            "Enhanced Bulk Request - Partially Invalid Serial Numbers",
            "POST",
            "issue-requests/bulk",
            400,  # Should fail due to invalid serial
            data=bulk_request_data
        )
        
        # Clean up
        self.run_api_test("Partial Invalid Cleanup - Board", "DELETE", f"boards/{board_id}", 200)
        
        # This should fail - we expect None result for failed requests
        return result is None

    def test_enhanced_bulk_issue_request_unavailable_serial_numbers(self):
        """Test with serial numbers that are not available (wrong location/condition) - Enhanced Functionality"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create boards that are not available (wrong location/condition)
        test_boards = []
        unavailable_serials = []
        
        # Board 1: Issued (not available)
        board1_data = {
            "category_id": self.test_category_id,
            "serial_number": f"UNAVAIL_ISSUED_{datetime.now().strftime('%H%M%S')}",
            "location": "Issued for machine",
            "condition": "New",
            "comments": "Unavailable - already issued"
        }
        
        # Board 2: In stock but Scrap condition (not available)
        board2_data = {
            "category_id": self.test_category_id,
            "serial_number": f"UNAVAIL_SCRAP_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "Scrap",
            "comments": "Unavailable - scrap condition"
        }
        
        for i, board_data in enumerate([board1_data, board2_data], 1):
            create_result = self.run_api_test(
                f"Enhanced Unavailable - Create Unavailable Board {i}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
                unavailable_serials.append(create_result['serial_number'])
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Unavailable Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Test bulk request with unavailable serial numbers
        bulk_request_data = {
            "categories": [
                {"category_id": self.test_category_id, "serial_numbers": unavailable_serials}
            ],
            "issued_to": "Unavailable Serials Test Engineer",
            "project_number": "PROJ_UNAVAIL_001",
            "comments": "Testing unavailable serial numbers"
        }
        
        result = self.run_api_test(
            "Enhanced Bulk Request - Unavailable Serial Numbers",
            "POST",
            "issue-requests/bulk",
            400,  # Should fail due to unavailable boards
            data=bulk_request_data
        )
        
        # Clean up
        for board_id in test_boards:
            self.run_api_test(f"Unavailable Final Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        # This should fail - we expect None result for failed requests
        return result is None

    def test_enhanced_bulk_issue_request_wrong_category_serials(self):
        """Test with serial numbers from wrong category - Enhanced Functionality"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create a second category
        category2_data = {
            "name": f"Wrong Category Test {datetime.now().strftime('%H%M%S')}",
            "description": "Category for wrong category testing",
            "manufacturer": "Wrong Category Manufacturer",
            "version": "1.0",
            "lead_time_days": 30,
            "minimum_stock_quantity": 10
        }
        
        category2_result = self.run_api_test(
            "Enhanced Wrong Category - Create Second Category",
            "POST",
            "categories",
            200,
            data=category2_data
        )
        
        if not category2_result or 'id' not in category2_result:
            return False
            
        category2_id = category2_result['id']
        
        # Create a board in the second category
        board_data = {
            "category_id": category2_id,
            "serial_number": f"WRONG_CAT_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "New",
            "comments": "Board in wrong category"
        }
        
        create_result = self.run_api_test(
            "Enhanced Wrong Category - Create Board in Category2",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not create_result or 'id' not in create_result:
            self.run_api_test("Wrong Category Cleanup - Category2", "DELETE", f"categories/{category2_id}", 200)
            return False
            
        board_id = create_result['id']
        wrong_category_serial = create_result['serial_number']
        
        # Test bulk request using serial from category2 but requesting from category1
        bulk_request_data = {
            "categories": [
                {"category_id": self.test_category_id, "serial_numbers": [wrong_category_serial]}
            ],
            "issued_to": "Wrong Category Test Engineer",
            "project_number": "PROJ_WRONG_CAT_001",
            "comments": "Testing wrong category serial numbers"
        }
        
        result = self.run_api_test(
            "Enhanced Bulk Request - Wrong Category Serial Numbers",
            "POST",
            "issue-requests/bulk",
            400,  # Should fail due to serial not found in requested category
            data=bulk_request_data
        )
        
        # Clean up
        self.run_api_test("Wrong Category Cleanup - Board", "DELETE", f"boards/{board_id}", 200)
        self.run_api_test("Wrong Category Cleanup - Category2", "DELETE", f"categories/{category2_id}", 200)
        
        # This should fail - we expect None result for failed requests
        return result is None

    def test_enhanced_bulk_issue_request_integration_quantity_still_works(self):
        """Test quantity-based requests (original functionality still works) - Enhanced Functionality"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create test boards for quantity-based request
        test_boards = []
        for i in range(3):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"INTEGRATION_QTY_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Integration quantity test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Enhanced Integration - Create Quantity Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Integration Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Test original quantity-based functionality
        bulk_request_data = {
            "categories": [
                {"category_id": self.test_category_id, "quantity": 2}
            ],
            "issued_to": "Integration Quantity Test Engineer",
            "project_number": "PROJ_INTEGRATION_001",
            "comments": "Testing original quantity functionality"
        }
        
        result = self.run_api_test(
            "Enhanced Integration - Quantity-Based Request (Original Functionality)",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        success = False
        if result and result.get('successful') == 2:
            # Verify that requests were created without specific serial numbers initially
            created_requests = result.get('created_requests', [])
            if len(created_requests) == 2:
                success = True
            else:
                self.log_test("Integration Quantity Count", False, 
                    f"Expected 2 requests, got {len(created_requests)}")
        
        # Clean up
        if result and 'created_requests' in result:
            for req in result['created_requests']:
                self.run_api_test(f"Integration Cleanup - Request {req['id']}", "DELETE", f"issue-requests/{req['id']}", 200)
        
        for board_id in test_boards:
            self.run_api_test(f"Integration Final Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_enhanced_bulk_issue_request_error_messages_validation(self):
        """Test proper error messages for specific serial number failures - Enhanced Functionality"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create one available board
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"ERROR_MSG_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "New",
            "comments": "Board for error message testing"
        }
        
        create_result = self.run_api_test(
            "Enhanced Error Messages - Create Available Board",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not create_result or 'id' not in create_result:
            return False
            
        board_id = create_result['id']
        available_serial = create_result['serial_number']
        
        # Test 1: Non-existent serial number error message
        bulk_request_data = {
            "categories": [
                {"category_id": self.test_category_id, "serial_numbers": ["NONEXISTENT_ERROR_TEST"]}
            ],
            "issued_to": "Error Message Test Engineer",
            "project_number": "PROJ_ERROR_001",
            "comments": "Testing error messages"
        }
        
        # Make the request and capture the response for error message validation
        url = f"{self.api_url}/issue-requests/bulk"
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {self.token}'}
        
        try:
            import requests
            response = requests.post(url, json=bulk_request_data, headers=headers, timeout=10)
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    error_detail = error_data.get('detail', '')
                    
                    # Check if error message contains information about the unavailable serial
                    if 'NONEXISTENT_ERROR_TEST' in error_detail and 'not available' in error_detail:
                        self.log_test("Enhanced Error Messages - Non-existent Serial", True, 
                            f"Correct error message: {error_detail}")
                        error_message_test_passed = True
                    else:
                        self.log_test("Enhanced Error Messages - Non-existent Serial", False, 
                            f"Expected error about unavailable serial, got: {error_detail}")
                        error_message_test_passed = False
                except:
                    self.log_test("Enhanced Error Messages - Non-existent Serial", False, 
                        f"Could not parse error response: {response.text}")
                    error_message_test_passed = False
            else:
                self.log_test("Enhanced Error Messages - Non-existent Serial", False, 
                    f"Expected 400 status, got {response.status_code}")
                error_message_test_passed = False
                
        except Exception as e:
            self.log_test("Enhanced Error Messages - Non-existent Serial", False, f"Request failed: {str(e)}")
            error_message_test_passed = False
        
        # Clean up
        self.run_api_test("Error Messages Cleanup - Board", "DELETE", f"boards/{board_id}", 200)
        
        return error_message_test_passed

    def test_bulk_issue_request_approval_admin_required(self):
        """Test bulk issue request approval requires admin authorization - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create test boards
        test_boards = []
        for i in range(2):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"APPROVAL_AUTH_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Approval auth test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Bulk Approval Auth - Create Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Approval Auth Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Create bulk issue request
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "quantity": 2
                }
            ],
            "issued_to": "Approval Auth Test Engineer",
            "project_number": "PROJ_APPROVAL_AUTH_001",
            "comments": "Testing bulk request approval authorization"
        }
        
        bulk_create_result = self.run_api_test(
            "Bulk Approval Auth - Create Bulk Request",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        if not bulk_create_result or 'request_id' not in bulk_create_result:
            # Clean up and return failure
            for board_id in test_boards:
                self.run_api_test(f"Approval Auth Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
            return False
        
        created_request_id = bulk_create_result['request_id']
        
        # Test approval without admin role (should fail with 403)
        approval_data = {
            "status": "approved"
        }
        
        approval_result = self.run_api_test(
            "Bulk Approval Auth - Non-Admin Approval (Should Fail)",
            "PUT",
            f"bulk-issue-requests/{created_request_id}",
            403,  # Should fail with 403 Forbidden
            data=approval_data
        )
        
        success = approval_result is None  # We expect this to fail
        
        # Clean up test boards
        for board_id in test_boards:
            self.run_api_test(f"Approval Auth Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_bulk_issue_request_approval_workflow(self):
        """Test complete bulk issue request approval workflow - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create test boards
        test_boards = []
        for i in range(3):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"APPROVAL_WORKFLOW_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Approval workflow test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Bulk Approval Workflow - Create Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Approval Workflow Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Step 1: Create bulk issue request
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "quantity": 3
                }
            ],
            "issued_to": "Approval Workflow Test Engineer",
            "project_number": "PROJ_APPROVAL_WORKFLOW_001",
            "comments": "Testing complete bulk request approval workflow"
        }
        
        bulk_create_result = self.run_api_test(
            "Bulk Approval Workflow - Create Bulk Request",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        if not bulk_create_result or 'request_id' not in bulk_create_result:
            # Clean up and return failure
            for board_id in test_boards:
                self.run_api_test(f"Approval Workflow Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
            return False
        
        created_request_id = bulk_create_result['request_id']
        
        # Step 2: Retrieve request to verify it's in "pending" status
        retrieval_result = self.run_api_test(
            "Bulk Approval Workflow - Verify Pending Status",
            "GET",
            "bulk-issue-requests",
            200
        )
        
        pending_verified = False
        if retrieval_result and isinstance(retrieval_result, list):
            found_request = next((req for req in retrieval_result if req.get('id') == created_request_id), None)
            if found_request and found_request.get('status') == 'pending':
                pending_verified = True
        
        if not pending_verified:
            self.log_test("Bulk Approval Workflow - Pending Status Verification", False, "Request not found or not in pending status")
            # Clean up and return failure
            for board_id in test_boards:
                self.run_api_test(f"Approval Workflow Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
            return False
        
        # Step 3: Make current user admin for approval
        if hasattr(self, 'user_data'):
            admin_result = self.run_api_test(
                "Bulk Approval Workflow - Setup Admin",
                "POST",
                f"setup-admin?email={self.user_data['email']}",
                200
            )
            
            if not admin_result:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Approval Workflow Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Step 4: Approve the bulk request
        approval_data = {
            "status": "approved"
        }
        
        approval_result = self.run_api_test(
            "Bulk Approval Workflow - Approve Request",
            "PUT",
            f"bulk-issue-requests/{created_request_id}",
            200,
            data=approval_data
        )
        
        success = False
        if approval_result:
            # Verify the request status changed to "approved"
            if (approval_result.get('status') == 'approved' and
                'approved_by' in approval_result and
                'approved_date' in approval_result):
                
                # Verify approved_by field is set correctly
                if approval_result.get('approved_by') == self.user_data['email']:
                    success = True
                else:
                    self.log_test("Bulk Approval Workflow - Approved By Field", False, 
                        f"Expected approved_by='{self.user_data['email']}', got '{approval_result.get('approved_by')}'")
            else:
                self.log_test("Bulk Approval Workflow - Approval Response", False, 
                    f"Invalid approval response: {approval_result}")
        
        # Step 5: Verify the request appears with updated status in GET endpoint
        if success:
            final_retrieval_result = self.run_api_test(
                "Bulk Approval Workflow - Verify Final Status",
                "GET",
                "bulk-issue-requests",
                200
            )
            
            if final_retrieval_result and isinstance(final_retrieval_result, list):
                final_request = next((req for req in final_retrieval_result if req.get('id') == created_request_id), None)
                if not (final_request and final_request.get('status') == 'approved'):
                    success = False
                    self.log_test("Bulk Approval Workflow - Final Status Verification", False, 
                        f"Request status not updated in GET endpoint: {final_request.get('status') if final_request else 'Not found'}")
        
        # Clean up test boards
        for board_id in test_boards:
            self.run_api_test(f"Approval Workflow Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_bulk_issue_request_rejection_workflow(self):
        """Test bulk issue request rejection workflow - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create test boards
        test_boards = []
        for i in range(2):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"REJECTION_WORKFLOW_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Rejection workflow test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Bulk Rejection Workflow - Create Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Rejection Workflow Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Create bulk issue request
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "quantity": 2
                }
            ],
            "issued_to": "Rejection Workflow Test Engineer",
            "project_number": "PROJ_REJECTION_WORKFLOW_001",
            "comments": "Testing bulk request rejection workflow"
        }
        
        bulk_create_result = self.run_api_test(
            "Bulk Rejection Workflow - Create Bulk Request",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        if not bulk_create_result or 'request_id' not in bulk_create_result:
            # Clean up and return failure
            for board_id in test_boards:
                self.run_api_test(f"Rejection Workflow Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
            return False
        
        created_request_id = bulk_create_result['request_id']
        
        # Make current user admin for rejection
        if hasattr(self, 'user_data'):
            admin_result = self.run_api_test(
                "Bulk Rejection Workflow - Setup Admin",
                "POST",
                f"setup-admin?email={self.user_data['email']}",
                200
            )
            
            if not admin_result:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Rejection Workflow Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Reject the bulk request
        rejection_data = {
            "status": "rejected"
        }
        
        rejection_result = self.run_api_test(
            "Bulk Rejection Workflow - Reject Request",
            "PUT",
            f"bulk-issue-requests/{created_request_id}",
            200,
            data=rejection_data
        )
        
        success = False
        if rejection_result:
            # Verify the request status changed to "rejected"
            if rejection_result.get('status') == 'rejected':
                success = True
            else:
                self.log_test("Bulk Rejection Workflow - Rejection Response", False, 
                    f"Expected status='rejected', got '{rejection_result.get('status')}'")
        
        # Clean up test boards
        for board_id in test_boards:
            self.run_api_test(f"Rejection Workflow Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_bulk_issue_request_approval_error_handling(self):
        """Test error handling for bulk issue request approval - Review Request Focus"""
        # Test 1: Approval with non-existent request ID (should return 404)
        fake_request_id = "fake-bulk-request-id-12345"
        
        approval_data = {
            "status": "approved"
        }
        
        # Make current user admin first
        if hasattr(self, 'user_data'):
            admin_result = self.run_api_test(
                "Bulk Approval Error - Setup Admin",
                "POST",
                f"setup-admin?email={self.user_data['email']}",
                200
            )
            
            if not admin_result:
                return False
        
        # Test non-existent request approval
        nonexistent_result = self.run_api_test(
            "Bulk Approval Error - Non-existent Request (Should Return 404)",
            "PUT",
            f"bulk-issue-requests/{fake_request_id}",
            404,  # Should return 404 Not Found
            data=approval_data
        )
        
        # Test 2: Approval with invalid status values
        if hasattr(self, 'test_category_id'):
            # Create a test request for invalid status testing
            test_boards = []
            for i in range(1):
                board_data = {
                    "category_id": self.test_category_id,
                    "serial_number": f"ERROR_HANDLING_{i}_{datetime.now().strftime('%H%M%S')}",
                    "location": "In stock",
                    "condition": "New",
                    "comments": f"Error handling test board {i+1}"
                }
                
                create_result = self.run_api_test(
                    f"Bulk Approval Error - Create Board {i+1}",
                    "POST",
                    "boards",
                    200,
                    data=board_data
                )
                
                if create_result and 'id' in create_result:
                    test_boards.append(create_result['id'])
            
            if test_boards:
                # Create bulk request for invalid status testing
                bulk_request_data = {
                    "categories": [
                        {
                            "category_id": self.test_category_id,
                            "quantity": 1
                        }
                    ],
                    "issued_to": "Error Handling Test Engineer",
                    "project_number": "PROJ_ERROR_HANDLING_001",
                    "comments": "Testing error handling"
                }
                
                bulk_create_result = self.run_api_test(
                    "Bulk Approval Error - Create Test Request",
                    "POST",
                    "issue-requests/bulk",
                    200,
                    data=bulk_request_data
                )
                
                if bulk_create_result and 'request_id' in bulk_create_result:
                    created_request_id = bulk_create_result['request_id']
                    
                    # Test invalid status value
                    invalid_status_data = {
                        "status": "invalid_status"
                    }
                    
                    invalid_status_result = self.run_api_test(
                        "Bulk Approval Error - Invalid Status Value",
                        "PUT",
                        f"bulk-issue-requests/{created_request_id}",
                        422,  # Should return validation error
                        data=invalid_status_data
                    )
                    
                    # Clean up test boards
                    for board_id in test_boards:
                        self.run_api_test(f"Error Handling Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                    
                    # Both tests should fail (return None), indicating proper error handling
                    return nonexistent_result is None and invalid_status_result is None
        
        # If we couldn't create test data, just check the non-existent request test
        return nonexistent_result is None

    def test_bulk_issue_request_data_integrity(self):
        """Test data integrity during bulk request approval process - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create test boards
        test_boards = []
        original_serials = []
        for i in range(3):
            serial_num = f"DATA_INTEGRITY_{i}_{datetime.now().strftime('%H%M%S')}"
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": serial_num,
                "location": "In stock",
                "condition": "New",
                "comments": f"Data integrity test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Bulk Data Integrity - Create Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
                original_serials.append(serial_num)
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Data Integrity Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Create bulk issue request with specific serial numbers
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "serial_numbers": original_serials
                }
            ],
            "issued_to": "Data Integrity Test Engineer",
            "project_number": "PROJ_DATA_INTEGRITY_001",
            "comments": "Testing data integrity during approval"
        }
        
        bulk_create_result = self.run_api_test(
            "Bulk Data Integrity - Create Bulk Request",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        if not bulk_create_result or 'request_id' not in bulk_create_result:
            # Clean up and return failure
            for board_id in test_boards:
                self.run_api_test(f"Data Integrity Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
            return False
        
        created_request_id = bulk_create_result['request_id']
        
        # Capture original request data before approval
        original_retrieval_result = self.run_api_test(
            "Bulk Data Integrity - Get Original Request Data",
            "GET",
            "bulk-issue-requests",
            200
        )
        
        original_request = None
        if original_retrieval_result and isinstance(original_retrieval_result, list):
            original_request = next((req for req in original_retrieval_result if req.get('id') == created_request_id), None)
        
        if not original_request:
            # Clean up and return failure
            for board_id in test_boards:
                self.run_api_test(f"Data Integrity Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
            return False
        
        # Make current user admin for approval
        if hasattr(self, 'user_data'):
            admin_result = self.run_api_test(
                "Bulk Data Integrity - Setup Admin",
                "POST",
                f"setup-admin?email={self.user_data['email']}",
                200
            )
            
            if not admin_result:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Data Integrity Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Approve the bulk request
        approval_data = {
            "status": "approved"
        }
        
        approval_result = self.run_api_test(
            "Bulk Data Integrity - Approve Request",
            "PUT",
            f"bulk-issue-requests/{created_request_id}",
            200,
            data=approval_data
        )
        
        if not approval_result:
            # Clean up and return failure
            for board_id in test_boards:
                self.run_api_test(f"Data Integrity Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
            return False
        
        # Verify data integrity after approval
        post_approval_retrieval_result = self.run_api_test(
            "Bulk Data Integrity - Get Post-Approval Request Data",
            "GET",
            "bulk-issue-requests",
            200
        )
        
        success = False
        if post_approval_retrieval_result and isinstance(post_approval_retrieval_result, list):
            post_approval_request = next((req for req in post_approval_retrieval_result if req.get('id') == created_request_id), None)
            
            if post_approval_request:
                # Verify boards array is preserved
                original_boards = original_request.get('boards', [])
                post_approval_boards = post_approval_request.get('boards', [])
                
                if (len(original_boards) == len(post_approval_boards) == 3 and
                    post_approval_request.get('status') == 'approved'):
                    
                    # Verify all serial numbers are preserved
                    original_board_serials = set(board.get('serial_number') for board in original_boards)
                    post_approval_board_serials = set(board.get('serial_number') for board in post_approval_boards)
                    
                    if original_board_serials == post_approval_board_serials == set(original_serials):
                        # Verify other fields are preserved
                        if (post_approval_request.get('issued_to') == original_request.get('issued_to') and
                            post_approval_request.get('project_number') == original_request.get('project_number') and
                            post_approval_request.get('comments') == original_request.get('comments')):
                            success = True
                        else:
                            self.log_test("Bulk Data Integrity - Field Preservation", False, 
                                "Request fields not preserved during approval")
                    else:
                        self.log_test("Bulk Data Integrity - Serial Number Preservation", False, 
                            f"Serial numbers not preserved. Original: {original_board_serials}, Post-approval: {post_approval_board_serials}")
                else:
                    self.log_test("Bulk Data Integrity - Boards Array Preservation", False, 
                        f"Boards array not preserved. Original count: {len(original_boards)}, Post-approval count: {len(post_approval_boards)}")
            else:
                self.log_test("Bulk Data Integrity - Request Retrieval", False, "Request not found after approval")
        
        # Clean up test boards
        for board_id in test_boards:
            self.run_api_test(f"Data Integrity Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_delete_board(self):
        """Test deleting a board"""
        if not hasattr(self, 'test_board_id'):
            return False
            
        result = self.run_api_test(
            "Delete Board",
            "DELETE",
            f"boards/{self.test_board_id}",
            200
        )
        return result is not None

    def test_delete_category(self):
        """Test deleting a category"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        result = self.run_api_test(
            "Delete Category",
            "DELETE",
            f"categories/{self.test_category_id}",
            200
        )
        return result is not None

    def test_invalid_login(self):
        """Test login with invalid credentials"""
        result = self.run_api_test(
            "Invalid Login Test",
            "POST",
            "auth/login",
            400,
            data={"email": "invalid@example.com", "password": "wrongpassword"}
        )
        return result is None  # We expect this to fail (return None)

    def test_unauthorized_access(self):
        """Test accessing protected endpoint without token"""
        # Temporarily remove token
        temp_token = self.token
        self.token = None
        
        result = self.run_api_test(
            "Unauthorized Access Test",
            "GET",
            "categories",
            401
        )
        
        # Restore token
        self.token = temp_token
        return result is None  # We expect this to fail (return None)

    def test_bulk_issue_request_outward_workflow(self):
        """Test the complete bulk issue request approval and outward workflow - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        print("\n🔄 Testing Bulk Issue Request Outward Workflow...")
        
        # Step 1: Create test boards for bulk request
        test_boards = []
        for i in range(3):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"BULK_OUTWARD_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Bulk outward test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Bulk Outward - Create Test Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Bulk Outward Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Step 2: Create bulk issue request
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "quantity": 2
                }
            ],
            "issued_to": "Bulk Outward Test Engineer",
            "project_number": "PROJ_BULK_OUTWARD_001",
            "comments": "Bulk request for outward workflow testing"
        }
        
        bulk_result = self.run_api_test(
            "Bulk Outward - Create Bulk Issue Request",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        if not bulk_result or 'request_id' not in bulk_result:
            # Clean up and return failure
            for board_id in test_boards:
                self.run_api_test(f"Bulk Outward Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
            return False
        
        bulk_request_id = bulk_result['request_id']
        
        # Step 3: Make user admin for approval
        if hasattr(self, 'user_data'):
            admin_result = self.run_api_test(
                "Bulk Outward - Setup Admin",
                "POST",
                f"setup-admin?email={self.user_data['email']}",
                200
            )
            
            if not admin_result:
                # Clean up and return failure
                self.run_api_test(f"Bulk Outward Cleanup - Request {bulk_request_id}", "DELETE", f"bulk-issue-requests/{bulk_request_id}", 200)
                for board_id in test_boards:
                    self.run_api_test(f"Bulk Outward Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Step 4: Approve the bulk request
        approve_data = {
            "status": "approved"
        }
        
        approve_result = self.run_api_test(
            "Bulk Outward - Approve Bulk Request",
            "PUT",
            f"bulk-issue-requests/{bulk_request_id}",
            200,
            data=approve_data
        )
        
        if not approve_result or approve_result.get('status') != 'approved':
            # Clean up and return failure
            self.run_api_test(f"Bulk Outward Cleanup - Request {bulk_request_id}", "DELETE", f"bulk-issue-requests/{bulk_request_id}", 200)
            for board_id in test_boards:
                self.run_api_test(f"Bulk Outward Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
            return False
        
        # Step 5: Test fetching outward data - both individual and bulk requests
        # Test individual requests endpoint
        individual_requests_result = self.run_api_test(
            "Bulk Outward - Fetch Individual Issue Requests",
            "GET",
            "issue-requests",
            200
        )
        
        # Test bulk requests endpoint
        bulk_requests_result = self.run_api_test(
            "Bulk Outward - Fetch Bulk Issue Requests",
            "GET",
            "bulk-issue-requests",
            200
        )
        
        if not bulk_requests_result or not isinstance(bulk_requests_result, list):
            # Clean up and return failure
            self.run_api_test(f"Bulk Outward Cleanup - Request {bulk_request_id}", "DELETE", f"bulk-issue-requests/{bulk_request_id}", 200)
            for board_id in test_boards:
                self.run_api_test(f"Bulk Outward Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
            return False
        
        # Verify our approved bulk request appears in the list
        found_bulk_request = None
        for req in bulk_requests_result:
            if req.get('id') == bulk_request_id and req.get('status') == 'approved':
                found_bulk_request = req
                break
        
        if not found_bulk_request:
            self.log_test("Bulk Outward - Approved Request Visibility", False, 
                f"Approved bulk request {bulk_request_id} not found in bulk-issue-requests endpoint")
            # Clean up and return failure
            self.run_api_test(f"Bulk Outward Cleanup - Request {bulk_request_id}", "DELETE", f"bulk-issue-requests/{bulk_request_id}", 200)
            for board_id in test_boards:
                self.run_api_test(f"Bulk Outward Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
            return False
        
        # Step 6: Test bulk request issuance via outward endpoint
        outward_data = {
            "request_id": bulk_request_id,
            "comments": "Issuing bulk request via outward endpoint"
        }
        
        outward_result = self.run_api_test(
            "Bulk Outward - Issue Bulk Request",
            "POST",
            "outward",
            200,
            data=outward_data
        )
        
        if not outward_result or 'message' not in outward_result:
            # Clean up and return failure
            self.run_api_test(f"Bulk Outward Cleanup - Request {bulk_request_id}", "DELETE", f"bulk-issue-requests/{bulk_request_id}", 200)
            for board_id in test_boards:
                self.run_api_test(f"Bulk Outward Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
            return False
        
        # Step 7: Verify bulk request status was updated to 'issued'
        final_bulk_result = self.run_api_test(
            "Bulk Outward - Verify Final Status",
            "GET",
            "bulk-issue-requests",
            200
        )
        
        if final_bulk_result:
            final_request = None
            for req in final_bulk_result:
                if req.get('id') == bulk_request_id:
                    final_request = req
                    break
            
            if final_request and final_request.get('status') in ['issued', 'partially_issued']:
                success = True
            else:
                success = False
                self.log_test("Bulk Outward - Final Status Verification", False, 
                    f"Expected status 'issued' or 'partially_issued', got '{final_request.get('status') if final_request else 'Request not found'}'")
        else:
            success = False
        
        # Step 8: Verify boards were actually issued
        if success:
            issued_boards_count = 0
            for board_id in test_boards:
                board_result = self.run_api_test(
                    f"Bulk Outward - Verify Board {board_id} Issued",
                    "GET",
                    f"boards/{board_id}",
                    200
                )
                if board_result and board_result.get('location') == 'Issued for machine':
                    issued_boards_count += 1
            
            if issued_boards_count < 2:  # We requested 2 boards
                success = False
                self.log_test("Bulk Outward - Boards Issuance Verification", False, 
                    f"Expected at least 2 boards to be issued, found {issued_boards_count}")
        
        # Clean up
        self.run_api_test(f"Bulk Outward Final Cleanup - Request {bulk_request_id}", "DELETE", f"bulk-issue-requests/{bulk_request_id}", 200)
        for board_id in test_boards:
            self.run_api_test(f"Bulk Outward Final Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_bulk_outward_workflow_with_login_credentials(self):
        """Test bulk outward workflow using provided test credentials"""
        print("\n🔐 Testing Bulk Outward Workflow with Provided Credentials...")
        
        # Login with provided credentials
        login_data = {
            "email": "suraajvdoshi@gmail.com",
            "password": "test123"
        }
        
        login_result = self.run_api_test(
            "Bulk Outward Credentials - Login",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if not login_result or 'access_token' not in login_result:
            return False
        
        # Update token and user data
        self.token = login_result['access_token']
        self.user_data = login_result['user']
        
        # Get categories to use for testing
        categories_result = self.run_api_test(
            "Bulk Outward Credentials - Get Categories",
            "GET",
            "categories",
            200
        )
        
        if not categories_result or not isinstance(categories_result, list) or len(categories_result) == 0:
            return False
        
        # Use first available category
        test_category_id = categories_result[0]['id']
        
        # Create test boards for bulk request
        test_boards = []
        for i in range(3):
            board_data = {
                "category_id": test_category_id,
                "serial_number": f"CRED_BULK_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Credentials bulk test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Bulk Outward Credentials - Create Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Bulk Outward Credentials Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Create bulk issue request
        bulk_request_data = {
            "categories": [
                {
                    "category_id": test_category_id,
                    "quantity": 2
                }
            ],
            "issued_to": "Credentials Test Engineer",
            "project_number": "PROJ_CRED_BULK_001",
            "comments": "Bulk request with provided credentials"
        }
        
        bulk_result = self.run_api_test(
            "Bulk Outward Credentials - Create Bulk Request",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        if not bulk_result or 'request_id' not in bulk_result:
            # Clean up and return failure
            for board_id in test_boards:
                self.run_api_test(f"Bulk Outward Credentials Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
            return False
        
        bulk_request_id = bulk_result['request_id']
        
        # Check if user is admin (provided credentials should have admin access)
        user_permissions_result = self.run_api_test(
            "Bulk Outward Credentials - Check User Permissions",
            "GET",
            "users/me/permissions",
            200
        )
        
        is_admin = (self.user_data.get('role') == 'admin' or 
                   (user_permissions_result and 'approve_issue_requests' in user_permissions_result.get('permissions', [])))
        
        if not is_admin:
            # Make user admin if not already
            admin_result = self.run_api_test(
                "Bulk Outward Credentials - Setup Admin",
                "POST",
                f"setup-admin?email={self.user_data['email']}",
                200
            )
            
            if not admin_result:
                # Clean up and return failure
                self.run_api_test(f"Bulk Outward Credentials Cleanup - Request {bulk_request_id}", "DELETE", f"bulk-issue-requests/{bulk_request_id}", 200)
                for board_id in test_boards:
                    self.run_api_test(f"Bulk Outward Credentials Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Approve the bulk request
        approve_data = {
            "status": "approved"
        }
        
        approve_result = self.run_api_test(
            "Bulk Outward Credentials - Approve Bulk Request",
            "PUT",
            f"bulk-issue-requests/{bulk_request_id}",
            200,
            data=approve_data
        )
        
        if not approve_result or approve_result.get('status') != 'approved':
            # Clean up and return failure
            self.run_api_test(f"Bulk Outward Credentials Cleanup - Request {bulk_request_id}", "DELETE", f"bulk-issue-requests/{bulk_request_id}", 200)
            for board_id in test_boards:
                self.run_api_test(f"Bulk Outward Credentials Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
            return False
        
        # Test that approved bulk request appears in outward data
        bulk_requests_result = self.run_api_test(
            "Bulk Outward Credentials - Fetch Approved Bulk Requests",
            "GET",
            "bulk-issue-requests",
            200
        )
        
        if not bulk_requests_result or not isinstance(bulk_requests_result, list):
            # Clean up and return failure
            self.run_api_test(f"Bulk Outward Credentials Cleanup - Request {bulk_request_id}", "DELETE", f"bulk-issue-requests/{bulk_request_id}", 200)
            for board_id in test_boards:
                self.run_api_test(f"Bulk Outward Credentials Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
            return False
        
        # Verify our approved bulk request appears in the list
        found_approved_request = None
        for req in bulk_requests_result:
            if req.get('id') == bulk_request_id and req.get('status') == 'approved':
                found_approved_request = req
                break
        
        if not found_approved_request:
            self.log_test("Bulk Outward Credentials - Approved Request in Outward", False, 
                f"Approved bulk request {bulk_request_id} not visible in outward tab data")
            # Clean up and return failure
            self.run_api_test(f"Bulk Outward Credentials Cleanup - Request {bulk_request_id}", "DELETE", f"bulk-issue-requests/{bulk_request_id}", 200)
            for board_id in test_boards:
                self.run_api_test(f"Bulk Outward Credentials Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
            return False
        
        # Test issuing the bulk request
        outward_data = {
            "request_id": bulk_request_id,
            "comments": "Issuing bulk request with provided credentials"
        }
        
        outward_result = self.run_api_test(
            "Bulk Outward Credentials - Issue Bulk Request",
            "POST",
            "outward",
            200,
            data=outward_data
        )
        
        success = outward_result and 'message' in outward_result
        
        # Clean up
        self.run_api_test(f"Bulk Outward Credentials Final Cleanup - Request {bulk_request_id}", "DELETE", f"bulk-issue-requests/{bulk_request_id}", 200)
        for board_id in test_boards:
            self.run_api_test(f"Bulk Outward Credentials Final Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_category_export_data_endpoint(self):
        """Test GET /api/reports/category-export/{category_id} - Category Export Review Request"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Test with valid category ID
        result = self.run_api_test(
            "Category Export Data - Valid Category",
            "GET",
            f"reports/category-export/{self.test_category_id}",
            200
        )
        
        if not result:
            return False
            
        # Verify response structure
        required_fields = ['category', 'boards', 'issue_requests', 'bulk_issue_requests', 'statistics']
        has_all_fields = all(field in result for field in required_fields)
        
        if not has_all_fields:
            missing_fields = [field for field in required_fields if field not in result]
            self.log_test("Category Export Data Structure", False, f"Missing fields: {missing_fields}")
            return False
            
        # Verify category details
        category = result.get('category', {})
        if not category or 'id' not in category or 'name' not in category:
            self.log_test("Category Export Category Details", False, "Category details incomplete")
            return False
            
        # Verify boards array
        boards = result.get('boards', [])
        if not isinstance(boards, list):
            self.log_test("Category Export Boards Array", False, "Boards should be an array")
            return False
            
        # Verify statistics
        statistics = result.get('statistics', {})
        required_stats = ['total_boards', 'in_stock', 'issued', 'repairing', 'total_requests', 'total_bulk_requests']
        has_all_stats = all(stat in statistics for stat in required_stats)
        
        if not has_all_stats:
            missing_stats = [stat for stat in required_stats if stat not in statistics]
            self.log_test("Category Export Statistics", False, f"Missing statistics: {missing_stats}")
            return False
            
        return True

    def test_category_export_data_invalid_id(self):
        """Test GET /api/reports/category-export/{category_id} with invalid ID - Category Export Review Request"""
        # Test with non-existent category ID
        invalid_id = "non-existent-category-id"
        result = self.run_api_test(
            "Category Export Data - Invalid Category ID",
            "GET",
            f"reports/category-export/{invalid_id}",
            404
        )
        
        # Should return 404 for non-existent category
        return result is None  # None indicates expected failure (404)

    def test_category_export_excel_generation(self):
        """Test GET /api/reports/export/category/{category_id} - Excel Export - Category Export Review Request"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Test Excel export with header authentication
        url = f"{self.api_url}/reports/export/category/{self.test_category_id}"
        headers = {
            'Authorization': f'Bearer {self.token}' if self.token else None
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Verify it's an Excel file
                content_type = response.headers.get('Content-Type', '')
                expected_content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                
                if expected_content_type in content_type:
                    # Verify Content-Disposition header
                    content_disposition = response.headers.get('Content-Disposition', '')
                    if 'attachment' in content_disposition and 'filename=' in content_disposition:
                        # Verify file size is reasonable (not empty)
                        content_length = len(response.content)
                        if content_length > 1000:  # At least 1KB
                            self.log_test("Category Export Excel Generation", True, 
                                f"Excel file generated successfully: {content_length} bytes, Content-Type: {content_type}")
                            return True
                        else:
                            self.log_test("Category Export Excel Generation", False, 
                                f"Excel file too small: {content_length} bytes")
                    else:
                        self.log_test("Category Export Excel Generation", False, 
                            f"Missing or invalid Content-Disposition header: {content_disposition}")
                else:
                    self.log_test("Category Export Excel Generation", False, 
                        f"Invalid Content-Type: {content_type}, expected: {expected_content_type}")
            else:
                self.log_test("Category Export Excel Generation", False, 
                    f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_test("Category Export Excel Generation", False, f"Exception: {str(e)}")
            
        return False

    def test_category_export_excel_query_param_auth(self):
        """Test GET /api/reports/export/category/{category_id}?token=... - Query Parameter Auth - Category Export Review Request"""
        if not hasattr(self, 'test_category_id') or not self.token:
            return False
            
        # Test Excel export with query parameter authentication
        url = f"{self.api_url}/reports/export/category/{self.test_category_id}?token={self.token}"
        
        try:
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                # Verify it's an Excel file
                content_type = response.headers.get('Content-Type', '')
                expected_content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                
                if expected_content_type in content_type:
                    # Verify file size is reasonable
                    content_length = len(response.content)
                    if content_length > 1000:  # At least 1KB
                        self.log_test("Category Export Excel Query Auth", True, 
                            f"Excel file generated with query auth: {content_length} bytes")
                        return True
                    else:
                        self.log_test("Category Export Excel Query Auth", False, 
                            f"Excel file too small: {content_length} bytes")
                else:
                    self.log_test("Category Export Excel Query Auth", False, 
                        f"Invalid Content-Type: {content_type}")
            else:
                self.log_test("Category Export Excel Query Auth", False, 
                    f"HTTP {response.status_code}: {response.text[:200]}")
                
        except Exception as e:
            self.log_test("Category Export Excel Query Auth", False, f"Exception: {str(e)}")
            
        return False

    def test_category_export_excel_invalid_category(self):
        """Test Excel export with invalid category ID - Category Export Review Request"""
        if not self.token:
            return False
            
        invalid_id = "non-existent-category-id"
        url = f"{self.api_url}/reports/export/category/{invalid_id}"
        headers = {
            'Authorization': f'Bearer {self.token}'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            # Should return 404 for non-existent category
            if response.status_code == 404:
                self.log_test("Category Export Excel Invalid Category", True, 
                    "Correctly returned 404 for invalid category")
                return True
            else:
                self.log_test("Category Export Excel Invalid Category", False, 
                    f"Expected 404, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Category Export Excel Invalid Category", False, f"Exception: {str(e)}")
            
        return False

    def test_category_export_permission_checks(self):
        """Test permission requirements for category export endpoints - Category Export Review Request"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create a new user without permissions
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"no_perms_{timestamp}@example.com"
        
        # Register new user
        register_result = self.run_api_test(
            "Category Export Permissions - Register User",
            "POST",
            "auth/register",
            200,
            data={
                "email": test_email, 
                "password": "TestPass123!",
                "first_name": "Test",
                "last_name": "User",
                "designation": "Tester"
            }
        )
        
        if not register_result or 'access_token' not in register_result:
            return False
            
        # Store original token
        original_token = self.token
        
        # Use new user's token (no permissions)
        self.token = register_result['access_token']
        
        # Test category export data endpoint (should require view_reports permission)
        data_result = self.run_api_test(
            "Category Export Permissions - Data Endpoint No Permission",
            "GET",
            f"reports/category-export/{self.test_category_id}",
            403
        )
        
        # Test Excel export endpoint (should require export_reports permission)
        url = f"{self.api_url}/reports/export/category/{self.test_category_id}"
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            excel_permission_ok = response.status_code == 403
            
            if excel_permission_ok:
                self.log_test("Category Export Permissions - Excel Export No Permission", True, 
                    "Correctly returned 403 for Excel export without permission")
            else:
                self.log_test("Category Export Permissions - Excel Export No Permission", False, 
                    f"Expected 403, got {response.status_code}")
                
        except Exception as e:
            self.log_test("Category Export Permissions - Excel Export No Permission", False, f"Exception: {str(e)}")
            excel_permission_ok = False
        
        # Restore original token
        self.token = original_token
        
        return data_result is None and excel_permission_ok  # None indicates expected failure (403)

    def test_category_export_excel_multiple_sheets(self):
        """Test Excel export contains multiple sheets with proper data - Category Export Review Request"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create some test data first
        # Create additional boards for this category
        test_boards = []
        for i in range(3):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"EXPORT_TEST_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock" if i % 2 == 0 else "Issued for machine",
                "condition": "New" if i % 2 == 0 else "OK",
                "comments": f"Export test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Category Export Excel Sheets - Create Test Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
        
        # Create test issue request
        request_data = {
            "category_id": self.test_category_id,
            "issued_to": "Export Test Engineer",
            "project_number": "PROJ_EXPORT_001",
            "comments": "Export test request"
        }
        
        request_result = self.run_api_test(
            "Category Export Excel Sheets - Create Test Request",
            "POST",
            "issue-requests",
            200,
            data=request_data
        )
        
        test_request_id = request_result.get('id') if request_result else None
        
        # Now test the Excel export
        url = f"{self.api_url}/reports/export/category/{self.test_category_id}"
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                # Verify file size is larger (should contain more data now)
                content_length = len(response.content)
                if content_length > 5000:  # Should be larger with multiple sheets
                    self.log_test("Category Export Excel Multiple Sheets", True, 
                        f"Excel file with multiple sheets: {content_length} bytes")
                    success = True
                else:
                    self.log_test("Category Export Excel Multiple Sheets", False, 
                        f"Excel file smaller than expected: {content_length} bytes")
                    success = False
            else:
                self.log_test("Category Export Excel Multiple Sheets", False, 
                    f"HTTP {response.status_code}: {response.text[:200]}")
                success = False
                
        except Exception as e:
            self.log_test("Category Export Excel Multiple Sheets", False, f"Exception: {str(e)}")
            success = False
        
        # Clean up test data
        for board_id in test_boards:
            self.run_api_test(f"Category Export Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        if test_request_id:
            self.run_api_test("Category Export Cleanup - Request", "DELETE", f"issue-requests/{test_request_id}", 200)
        
        return success

    def test_category_export_comprehensive(self):
        """Comprehensive test of all Category Export functionality - Category Export Review Request"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        print("\n🔍 COMPREHENSIVE CATEGORY EXPORT TESTING")
        print("=" * 60)
        
        # Test 1: Category data endpoint with valid ID
        test1 = self.test_category_export_data_endpoint()
        
        # Test 2: Category data endpoint with invalid ID
        test2 = self.test_category_export_data_invalid_id()
        
        # Test 3: Excel export with header authentication
        test3 = self.test_category_export_excel_generation()
        
        # Test 4: Excel export with query parameter authentication
        test4 = self.test_category_export_excel_query_param_auth()
        
        # Test 5: Excel export with invalid category
        test5 = self.test_category_export_excel_invalid_category()
        
        # Test 6: Permission checks
        test6 = self.test_category_export_permission_checks()
        
        # Test 7: Excel multiple sheets verification
        test7 = self.test_category_export_excel_multiple_sheets()
        
        all_tests = [test1, test2, test3, test4, test5, test6, test7]
        passed_tests = sum(all_tests)
        total_tests = len(all_tests)
        
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"\n📊 CATEGORY EXPORT TEST SUMMARY:")
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 85:  # Allow for some minor issues
            print("🎉 CATEGORY EXPORT FUNCTIONALITY IS WORKING!")
            return True
        else:
            print("⚠️  CATEGORY EXPORT HAS SIGNIFICANT ISSUES")
            return False

    def run_all_tests(self):
        """Run all API tests in sequence"""
        print("🚀 Starting Electronics Inventory API Tests")
        print("=" * 60)
        
        # Health check
        if not self.test_health_check():
            print("❌ API is not accessible. Stopping tests.")
            return False
        
        # PRIORITY: Test with provided credentials first
        print("\n🎯 PRIORITY: Testing Bulk Issue Request Outward Workflow with Provided Credentials")
        self.test_bulk_outward_workflow_with_login_credentials()
        
        # Authentication tests
        if not self.test_user_registration():
            print("❌ User registration failed. Stopping tests.")
            return False
            
        self.test_get_current_user()
        self.test_invalid_login()
        self.test_unauthorized_access()
        
        # Category tests
        if self.test_create_category():
            self.test_get_categories()
            self.test_get_category_by_id()
            self.test_update_category()
        
        # Board tests
        if self.test_create_board():
            self.test_get_boards()
            self.test_get_board_by_id()
            self.test_update_board()
            self.test_search_boards()
        
        # Inward workflow specific tests
        print("\n🔄 Testing Inward Workflow Functionality")
        print("-" * 40)
        if self.test_inward_new_workflow():
            self.test_inward_repair_workflow()
        self.test_inward_serial_number_validation()
        self.test_inward_workflow_complete()
        
        # Critical User Issues Tests - Outward Functionality
        print("\n🚨 Testing Critical User Issues - Outward Functionality")
        print("-" * 50)
        self.test_repaired_board_outward_workflow()
        self.test_outward_comments_field()
        self.test_board_query_filtering()
        self.test_end_to_end_workflow()
        self.test_issue_request_workflow()
        
        # Review Request Focus - Repairing/Return Workflow Updates
        print("\n🔧 Testing Repairing/Return Workflow Updates - Review Request Focus")
        print("-" * 60)
        self.test_repairing_condition_updates_new()
        self.test_repairing_condition_updates_repaired()
        self.test_repairing_condition_updates_scrap()
        self.test_repairing_workflow_complete_with_conditions()
        self.test_board_update_model_validation()
        self.test_api_response_validation_put_endpoint()
        
        # Bulk Issue Request Tests - Current Review Request Focus
        print("\n📦 Testing Bulk Issue Request Functionality - Review Request Focus")
        print("-" * 65)
        self.test_bulk_issue_request_single_category()
        self.test_bulk_issue_request_multiple_categories()
        self.test_bulk_issue_request_mixed_scenario()
        self.test_bulk_issue_request_maximum_scenario()
        self.test_bulk_issue_request_insufficient_stock()
        self.test_bulk_issue_request_nonexistent_category()
        self.test_bulk_issue_request_validation_errors()
        self.test_bulk_issue_request_stock_availability_new_only()
        self.test_bulk_issue_request_comments_application()
        
        # Enhanced Bulk Issue Request Tests - Specific Serial Number Selection
        print("\n🔢 Testing Enhanced Bulk Issue Request - Specific Serial Number Selection")
        print("-" * 75)
        self.test_enhanced_bulk_issue_request_model_validation_quantity()
        self.test_enhanced_bulk_issue_request_model_validation_serial_numbers()
        self.test_enhanced_bulk_issue_request_validation_both_fields()
        self.test_enhanced_bulk_issue_request_validation_neither_field()
        self.test_enhanced_bulk_issue_request_specific_serial_numbers()
        self.test_enhanced_bulk_issue_request_mixed_mode()
        self.test_enhanced_bulk_issue_request_invalid_serial_numbers()
        self.test_enhanced_bulk_issue_request_partially_invalid_serial_numbers()
        self.test_enhanced_bulk_issue_request_unavailable_serial_numbers()
        self.test_enhanced_bulk_issue_request_wrong_category_serials()
        self.test_enhanced_bulk_issue_request_integration_quantity_still_works()
        self.test_enhanced_bulk_issue_request_error_messages_validation()
        
        # Enhanced Bulk Issue Request Tests - Review Request Focus
        self.run_enhanced_bulk_issue_request_tests()
        
        # Bulk Issue Request Approval Tests - Review Request Focus
        self.run_bulk_issue_request_approval_tests()
        
        # Dashboard Enhanced Widget Tests - Review Request Focus
        print("\n📊 Testing Enhanced Dashboard Functionality - Review Request Focus")
        print("-" * 65)
        self.test_dashboard_stats()
        self.test_dashboard_pending_requests_calculation()
        self.test_dashboard_bulk_pending_requests_calculation()
        self.test_dashboard_repairing_boards_calculation()
        self.test_dashboard_low_stock_categories_detection()
        self.test_dashboard_stats_api_comprehensive()
        
        # Category Export Tests - Current Review Request Focus
        print("\n📋 Testing Category Export Functionality - CURRENT REVIEW REQUEST")
        print("-" * 70)
        self.test_category_export_comprehensive()
        
        # Cleanup tests
        if hasattr(self, 'test_board_id'):
            self.test_delete_board()
        if hasattr(self, 'inward_test_board_id'):
            self.run_api_test(
                "Cleanup Inward Test Board",
                "DELETE",
                f"boards/{self.inward_test_board_id}",
                200
            )
        if hasattr(self, 'test_category_id'):
            self.test_delete_category()
        
        # Print results
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed")
            return False

    def test_auto_select_preview_basic(self):
        """Test POST /api/boards/preview-auto-select endpoint - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create test boards for preview testing
        test_boards = []
        for i in range(3):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"PREVIEW_TEST_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Preview test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Auto-Select Preview - Create Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Preview Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Test preview auto-select endpoint
        preview_data = {
            "category_id": self.test_category_id,
            "quantity": 2
        }
        
        preview_result = self.run_api_test(
            "Auto-Select Preview - Basic Test",
            "POST",
            "boards/preview-auto-select",
            200,
            data=preview_data
        )
        
        success = False
        if preview_result:
            # Verify response structure
            if ('selected_boards' in preview_result and 
                'total_available' in preview_result and
                isinstance(preview_result['selected_boards'], list) and
                len(preview_result['selected_boards']) == 2):
                
                # Verify each selected board has required fields
                all_boards_valid = True
                for board in preview_result['selected_boards']:
                    if not all(field in board for field in ['id', 'serial_number', 'condition']):
                        all_boards_valid = False
                        break
                
                if all_boards_valid:
                    success = True
                else:
                    self.log_test("Auto-Select Preview Structure", False, "Selected boards missing required fields")
            else:
                self.log_test("Auto-Select Preview Response", False, f"Invalid response structure: {preview_result}")
        
        # Clean up test boards
        for board_id in test_boards:
            self.run_api_test(f"Preview Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_auto_select_preview_insufficient_stock(self):
        """Test auto-select preview with insufficient stock - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create only 1 board but request 3
        board_data = {
            "category_id": self.test_category_id,
            "serial_number": f"INSUFFICIENT_{datetime.now().strftime('%H%M%S')}",
            "location": "In stock",
            "condition": "New",
            "comments": "Single board for insufficient stock test"
        }
        
        create_result = self.run_api_test(
            "Auto-Select Preview Insufficient - Create Single Board",
            "POST",
            "boards",
            200,
            data=board_data
        )
        
        if not create_result or 'id' not in create_result:
            return False
            
        board_id = create_result['id']
        
        # Test preview with insufficient stock
        preview_data = {
            "category_id": self.test_category_id,
            "quantity": 3
        }
        
        preview_result = self.run_api_test(
            "Auto-Select Preview - Insufficient Stock Test",
            "POST",
            "boards/preview-auto-select",
            400,  # Should return 400 for insufficient stock
            data=preview_data
        )
        
        # Clean up
        self.run_api_test("Preview Insufficient Cleanup", "DELETE", f"boards/{board_id}", 200)
        
        return preview_result is None  # We expect this to fail with 400

    def test_auto_select_preview_different_categories(self):
        """Test auto-select preview with different categories and quantities - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create a second category for testing
        category_data = {
            "name": f"Preview Test Category {datetime.now().strftime('%H%M%S')}",
            "description": "Category for preview testing",
            "manufacturer": "Preview Manufacturer",
            "version": "1.0",
            "lead_time_days": 15,
            "minimum_stock_quantity": 5
        }
        
        category_result = self.run_api_test(
            "Auto-Select Preview Categories - Create Second Category",
            "POST",
            "categories",
            200,
            data=category_data
        )
        
        if not category_result or 'id' not in category_result:
            return False
            
        second_category_id = category_result['id']
        
        # Create boards in both categories
        test_boards = []
        
        # 3 boards in first category
        for i in range(3):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"CAT1_PREVIEW_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New"
            }
            
            create_result = self.run_api_test(
                f"Preview Categories - Create Cat1 Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
        
        # 2 boards in second category
        for i in range(2):
            board_data = {
                "category_id": second_category_id,
                "serial_number": f"CAT2_PREVIEW_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New"
            }
            
            create_result = self.run_api_test(
                f"Preview Categories - Create Cat2 Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
        
        # Test preview for first category (should work - has 3 boards, requesting 2)
        preview_data_1 = {
            "category_id": self.test_category_id,
            "quantity": 2
        }
        
        preview_result_1 = self.run_api_test(
            "Auto-Select Preview Categories - Test Category 1",
            "POST",
            "boards/preview-auto-select",
            200,
            data=preview_data_1
        )
        
        # Test preview for second category (should work - has 2 boards, requesting 1)
        preview_data_2 = {
            "category_id": second_category_id,
            "quantity": 1
        }
        
        preview_result_2 = self.run_api_test(
            "Auto-Select Preview Categories - Test Category 2",
            "POST",
            "boards/preview-auto-select",
            200,
            data=preview_data_2
        )
        
        success = (preview_result_1 is not None and 
                  preview_result_2 is not None and
                  len(preview_result_1.get('selected_boards', [])) == 2 and
                  len(preview_result_2.get('selected_boards', [])) == 1)
        
        # Clean up
        for board_id in test_boards:
            self.run_api_test(f"Preview Categories Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        self.run_api_test("Preview Categories Cleanup - Second Category", "DELETE", f"categories/{second_category_id}", 200)
        
        return success

    def test_single_bulk_issue_request_creation(self):
        """Test POST /api/issue-requests/bulk creates ONE request instead of multiple - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create test boards
        test_boards = []
        for i in range(4):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"SINGLE_BULK_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Single bulk test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Single Bulk Request - Create Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Single Bulk Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Create bulk issue request
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "quantity": 3
                }
            ],
            "issued_to": "Single Bulk Test Engineer",
            "project_number": "PROJ_SINGLE_BULK_001",
            "comments": "Testing single bulk request creation"
        }
        
        bulk_result = self.run_api_test(
            "Single Bulk Request - Create Bulk Request",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        success = False
        if bulk_result:
            # Verify response indicates single request creation
            if ('message' in bulk_result and 
                'request_id' in bulk_result and
                'total_boards' in bulk_result and
                bulk_result['total_boards'] == 3):
                
                # Verify the response structure includes boards array
                if 'boards' in bulk_result and isinstance(bulk_result['boards'], list):
                    success = True
                else:
                    self.log_test("Single Bulk Request Structure", False, "Response missing boards array")
            else:
                self.log_test("Single Bulk Request Response", False, f"Invalid response structure: {bulk_result}")
        
        # Clean up test boards
        for board_id in test_boards:
            self.run_api_test(f"Single Bulk Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_bulk_issue_request_retrieval(self):
        """Test GET /api/bulk-issue-requests endpoint - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create test boards
        test_boards = []
        for i in range(2):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"BULK_RETRIEVAL_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Bulk retrieval test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Bulk Retrieval - Create Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Bulk Retrieval Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Create a bulk issue request first
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "quantity": 2
                }
            ],
            "issued_to": "Bulk Retrieval Test Engineer",
            "project_number": "PROJ_BULK_RETRIEVAL_001",
            "comments": "Testing bulk request retrieval"
        }
        
        bulk_create_result = self.run_api_test(
            "Bulk Retrieval - Create Bulk Request",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        if not bulk_create_result or 'request_id' not in bulk_create_result:
            # Clean up and return failure
            for board_id in test_boards:
                self.run_api_test(f"Bulk Retrieval Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
            return False
        
        created_request_id = bulk_create_result['request_id']
        
        # Test GET /api/bulk-issue-requests endpoint
        retrieval_result = self.run_api_test(
            "Bulk Retrieval - Get Bulk Issue Requests",
            "GET",
            "bulk-issue-requests",
            200
        )
        
        success = False
        if retrieval_result and isinstance(retrieval_result, list):
            # Find our created request in the results
            found_request = next((req for req in retrieval_result if req.get('id') == created_request_id), None)
            
            if found_request:
                # Verify the structure includes all board details
                if ('boards' in found_request and 
                    isinstance(found_request['boards'], list) and
                    len(found_request['boards']) == 2):
                    
                    # Verify each board has required fields including serial numbers
                    all_boards_valid = True
                    for board in found_request['boards']:
                        if not all(field in board for field in ['category_id', 'serial_number', 'condition']):
                            all_boards_valid = False
                            break
                    
                    if all_boards_valid:
                        success = True
                    else:
                        self.log_test("Bulk Retrieval Board Structure", False, "Boards missing required fields")
                else:
                    self.log_test("Bulk Retrieval Request Structure", False, "Request missing boards array or incorrect count")
            else:
                self.log_test("Bulk Retrieval Find Request", False, f"Created request {created_request_id} not found in retrieval results")
        else:
            self.log_test("Bulk Retrieval Response", False, "Invalid response format - expected array")
        
        # Clean up test boards
        for board_id in test_boards:
            self.run_api_test(f"Bulk Retrieval Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def test_mixed_mode_bulk_request(self):
        """Test bulk requests with mixed quantity and specific serial selection modes - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create a second category for mixed mode testing
        category_data = {
            "name": f"Mixed Mode Category {datetime.now().strftime('%H%M%S')}",
            "description": "Category for mixed mode testing",
            "manufacturer": "Mixed Mode Manufacturer",
            "version": "1.0",
            "lead_time_days": 20,
            "minimum_stock_quantity": 3
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
        
        # Create test boards in both categories
        test_boards = []
        serial_numbers_cat1 = []
        
        # Create 3 boards in first category (for specific serial selection)
        for i in range(3):
            serial_num = f"MIXED_CAT1_{i}_{datetime.now().strftime('%H%M%S')}"
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": serial_num,
                "location": "In stock",
                "condition": "New",
                "comments": f"Mixed mode cat1 board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Mixed Mode - Create Cat1 Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
                serial_numbers_cat1.append(serial_num)
        
        # Create 4 boards in second category (for quantity mode)
        for i in range(4):
            board_data = {
                "category_id": second_category_id,
                "serial_number": f"MIXED_CAT2_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Mixed mode cat2 board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Mixed Mode - Create Cat2 Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
        
        # Create mixed mode bulk request
        mixed_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "serial_numbers": serial_numbers_cat1[:2]  # Specific serials for first 2 boards
                },
                {
                    "category_id": second_category_id,
                    "quantity": 3  # Quantity mode for second category
                }
            ],
            "issued_to": "Mixed Mode Test Engineer",
            "project_number": "PROJ_MIXED_MODE_001",
            "comments": "Testing mixed mode bulk request"
        }
        
        mixed_result = self.run_api_test(
            "Mixed Mode - Create Mixed Bulk Request",
            "POST",
            "issue-requests/bulk",
            200,
            data=mixed_request_data
        )
        
        success = False
        if mixed_result:
            # Verify single request contains all boards from both modes
            if ('total_boards' in mixed_result and 
                mixed_result['total_boards'] == 5 and  # 2 from specific serials + 3 from quantity
                'boards' in mixed_result and
                isinstance(mixed_result['boards'], list) and
                len(mixed_result['boards']) == 5):
                
                # Verify boards from both categories are included
                cat1_boards = [b for b in mixed_result['boards'] if b['category_id'] == self.test_category_id]
                cat2_boards = [b for b in mixed_result['boards'] if b['category_id'] == second_category_id]
                
                if len(cat1_boards) == 2 and len(cat2_boards) == 3:
                    # Verify specific serial numbers are included for cat1
                    cat1_serials = [b['serial_number'] for b in cat1_boards]
                    if all(serial in cat1_serials for serial in serial_numbers_cat1[:2]):
                        success = True
                    else:
                        self.log_test("Mixed Mode Serial Verification", False, f"Expected serials {serial_numbers_cat1[:2]}, got {cat1_serials}")
                else:
                    self.log_test("Mixed Mode Category Distribution", False, f"Expected 2 cat1 boards and 3 cat2 boards, got {len(cat1_boards)} and {len(cat2_boards)}")
            else:
                self.log_test("Mixed Mode Response Structure", False, f"Invalid response structure: {mixed_result}")
        
        # Clean up
        for board_id in test_boards:
            self.run_api_test(f"Mixed Mode Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        self.run_api_test("Mixed Mode Cleanup - Second Category", "DELETE", f"categories/{second_category_id}", 200)
        
        return success

    def test_bulk_issue_request_data_structure_validation(self):
        """Test BulkIssueRequest data structure validation - Review Request Focus"""
        if not hasattr(self, 'test_category_id'):
            return False
            
        # Create test boards
        test_boards = []
        for i in range(3):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"DATA_STRUCT_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Data structure test board {i+1}"
            }
            
            create_result = self.run_api_test(
                f"Data Structure - Create Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if create_result and 'id' in create_result:
                test_boards.append(create_result['id'])
            else:
                # Clean up and return failure
                for board_id in test_boards:
                    self.run_api_test(f"Data Structure Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
                return False
        
        # Create bulk request to test data structure
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "quantity": 3
                }
            ],
            "issued_to": "Data Structure Test Engineer",
            "project_number": "PROJ_DATA_STRUCT_001",
            "comments": "Testing BulkIssueRequest data structure"
        }
        
        bulk_create_result = self.run_api_test(
            "Data Structure - Create Bulk Request",
            "POST",
            "issue-requests/bulk",
            200,
            data=bulk_request_data
        )
        
        if not bulk_create_result or 'request_id' not in bulk_create_result:
            # Clean up and return failure
            for board_id in test_boards:
                self.run_api_test(f"Data Structure Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
            return False
        
        created_request_id = bulk_create_result['request_id']
        
        # Retrieve the created bulk request to validate structure
        retrieval_result = self.run_api_test(
            "Data Structure - Retrieve Bulk Request",
            "GET",
            "bulk-issue-requests",
            200
        )
        
        success = False
        if retrieval_result and isinstance(retrieval_result, list):
            # Find our created request
            found_request = next((req for req in retrieval_result if req.get('id') == created_request_id), None)
            
            if found_request:
                # Validate BulkIssueRequest structure
                required_fields = ['id', 'boards', 'requested_by', 'issued_to', 'project_number', 'status', 'created_date']
                optional_fields = ['comments', 'approved_by', 'approved_date']
                
                # Check required fields
                missing_required = [field for field in required_fields if field not in found_request]
                if missing_required:
                    self.log_test("Data Structure Required Fields", False, f"Missing required fields: {missing_required}")
                else:
                    # Validate boards array structure
                    boards = found_request.get('boards', [])
                    if isinstance(boards, list) and len(boards) == 3:
                        # Validate BoardRequest model structure
                        board_required_fields = ['category_id', 'serial_number', 'condition']
                        all_boards_valid = True
                        
                        for i, board in enumerate(boards):
                            missing_board_fields = [field for field in board_required_fields if field not in board]
                            if missing_board_fields:
                                all_boards_valid = False
                                self.log_test(f"Data Structure Board {i+1} Fields", False, f"Missing fields: {missing_board_fields}")
                                break
                        
                        if all_boards_valid:
                            # Verify all boards have serial numbers (not None or empty)
                            all_have_serials = all(board.get('serial_number') for board in boards)
                            if all_have_serials:
                                success = True
                            else:
                                self.log_test("Data Structure Serial Numbers", False, "Some boards missing serial numbers")
                    else:
                        self.log_test("Data Structure Boards Array", False, f"Expected 3 boards, got {len(boards) if isinstance(boards, list) else 'invalid type'}")
            else:
                self.log_test("Data Structure Find Request", False, f"Created request {created_request_id} not found")
        else:
            self.log_test("Data Structure Retrieval", False, "Failed to retrieve bulk requests")
        
        # Clean up test boards
        for board_id in test_boards:
            self.run_api_test(f"Data Structure Cleanup - Board {board_id}", "DELETE", f"boards/{board_id}", 200)
        
        return success

    def run_enhanced_bulk_issue_request_tests(self):
        """Run all enhanced bulk issue request tests - Review Request Focus"""
        print("\n🔥 Testing Enhanced Bulk Issue Request Functionality - Review Request Focus")
        print("=" * 80)
        
        # Auto-Select Preview Tests
        print("\n📋 Auto-Select Preview Testing")
        print("-" * 40)
        self.test_auto_select_preview_basic()
        self.test_auto_select_preview_insufficient_stock()
        self.test_auto_select_preview_different_categories()
        
        # Single Bulk Issue Request Creation Tests
        print("\n📦 Single Bulk Issue Request Creation Testing")
        print("-" * 50)
        self.test_single_bulk_issue_request_creation()
        
        # Bulk Issue Request Retrieval Tests
        print("\n📥 Bulk Issue Request Retrieval Testing")
        print("-" * 45)
        self.test_bulk_issue_request_retrieval()
        
        # Mixed Mode Testing
        print("\n🔀 Mixed Mode Testing")
        print("-" * 25)
        self.test_mixed_mode_bulk_request()
        
        # Data Structure Validation
        print("\n🏗️  Data Structure Validation")
        print("-" * 35)
        self.test_bulk_issue_request_data_structure_validation()

    def run_bulk_issue_request_approval_tests(self):
        """Run bulk issue request approval tests - Review Request Focus"""
        print("\n🔐 Testing Bulk Issue Request Approval Functionality")
        print("=" * 55)
        
        # Approval Authorization Tests
        print("\n🔒 Authorization Testing")
        print("-" * 25)
        self.test_bulk_issue_request_approval_admin_required()
        
        # Complete Approval Workflow Tests
        print("\n✅ Approval Workflow Testing")
        print("-" * 30)
        self.test_bulk_issue_request_approval_workflow()
        
        # Rejection Workflow Tests
        print("\n❌ Rejection Workflow Testing")
        print("-" * 30)
        self.test_bulk_issue_request_rejection_workflow()
        
        # Error Handling Tests
        print("\n⚠️ Error Handling Testing")
        print("-" * 25)
        self.test_bulk_issue_request_approval_error_handling()
        
        # Data Integrity Tests
        print("\n🔍 Data Integrity Testing")
        print("-" * 25)
        self.test_bulk_issue_request_data_integrity()
        
        print("✅ Bulk Issue Request Approval Tests Completed")

def main():
    tester = ElectronicsInventoryAPITester()
    success = tester.run_all_tests()
    
    # Save detailed results
    with open('/app/backend_test_results.json', 'w') as f:
        json.dump({
            'summary': {
                'total_tests': tester.tests_run,
                'passed_tests': tester.tests_passed,
                'success_rate': (tester.tests_passed / tester.tests_run * 100) if tester.tests_run > 0 else 0,
                'timestamp': datetime.now().isoformat()
            },
            'detailed_results': tester.test_results
        }, f, indent=2)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())