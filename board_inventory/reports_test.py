import requests
import sys
import json
from datetime import datetime

class ReportsAPITester:
    def __init__(self, base_url="https://boardventory.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.test_category_id = None
        self.test_board_id = None

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
                response = requests.get(url, headers=test_headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=test_headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=test_headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=test_headers, timeout=30)

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
                    return response  # Return response object for file downloads
            return None

        except Exception as e:
            self.log_test(name, False, f"Exception: {str(e)}")
            return None

    def test_login_with_provided_credentials(self):
        """Test login with provided credentials from review request"""
        result = self.run_api_test(
            "Login with Provided Credentials",
            "POST",
            "auth/login",
            200,
            data={
                "email": "suraajvdoshi@gmail.com",
                "password": "test123"
            }
        )
        
        if result and 'access_token' in result:
            self.token = result['access_token']
            self.user_data = result['user']
            return True
        return False

    def setup_test_data(self):
        """Create test category and boards for reports testing"""
        # Create test category
        category_data = {
            "name": f"Reports Test Category {datetime.now().strftime('%H%M%S')}",
            "description": "Category for reports functionality testing",
            "manufacturer": "Reports Test Manufacturer",
            "version": "1.0",
            "lead_time_days": 30,
            "minimum_stock_quantity": 5
        }
        
        category_result = self.run_api_test(
            "Setup - Create Test Category",
            "POST",
            "categories",
            200,
            data=category_data
        )
        
        if not category_result or 'id' not in category_result:
            return False
            
        self.test_category_id = category_result['id']
        
        # Create test boards with different conditions and locations
        board_configs = [
            ("In stock", "New", "Board 1 for reports testing"),
            ("In stock", "Repaired", "Board 2 for reports testing"), 
            ("Repairing", "Needs repair", "Board 3 under repair"),
            ("Repairing", "Repaired", "Board 4 repaired and ready"),
            ("Issued for machine", "New", "Board 5 issued to project"),
            ("At customer site", "Scrap", "Board 6 scrapped at customer")
        ]
        
        for i, (location, condition, comment) in enumerate(board_configs):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"REPORTS_TEST_{i+1}_{datetime.now().strftime('%H%M%S')}",
                "location": location,
                "condition": condition,
                "comments": comment
            }
            
            board_result = self.run_api_test(
                f"Setup - Create Test Board {i+1}",
                "POST",
                "boards",
                200,
                data=board_data
            )
            
            if board_result and 'id' in board_result and i == 0:
                self.test_board_id = board_result['id']
                self.test_serial_number = board_result['serial_number']
        
        return True

    def test_reports_low_stock(self):
        """Test GET /api/reports/low-stock endpoint"""
        result = self.run_api_test(
            "Reports - Low Stock Report",
            "GET",
            "reports/low-stock",
            200
        )
        
        if result is not None and isinstance(result, list):
            # Verify response structure for low stock items
            for item in result:
                required_fields = ['category_id', 'category_name', 'manufacturer', 'version', 
                                 'current_stock', 'minimum_stock_quantity', 'shortage_quantity']
                if not all(field in item for field in required_fields):
                    self.log_test("Low Stock Report Structure", False, f"Missing fields in response: {item}")
                    return False
            return True
        return False

    def test_reports_under_repair(self):
        """Test GET /api/reports/under-repair endpoint"""
        result = self.run_api_test(
            "Reports - Under Repair Report",
            "GET",
            "reports/under-repair",
            200
        )
        
        if result is not None and isinstance(result, list):
            # Verify response structure for under repair items
            for item in result:
                required_fields = ['serial_number', 'category_name', 'manufacturer', 'version', 
                                 'condition', 'location', 'inward_date', 'comments']
                if not all(field in item for field in required_fields):
                    self.log_test("Under Repair Report Structure", False, f"Missing fields in response: {item}")
                    return False
            return True
        return False

    def test_reports_serial_history(self):
        """Test GET /api/reports/serial-history/{serial_number} endpoint"""
        if not hasattr(self, 'test_serial_number'):
            return False
            
        result = self.run_api_test(
            "Reports - Serial History Report",
            "GET",
            f"reports/serial-history/{self.test_serial_number}",
            200
        )
        
        if result:
            # Verify response structure
            required_fields = ['serial_number', 'category_name', 'manufacturer', 'version', 
                             'current_status', 'issue_history', 'bulk_request_history', 'board_details']
            if all(field in result for field in required_fields):
                # Verify current_status structure
                status_fields = ['condition', 'location', 'issued_to', 'issued_by', 
                               'project_number', 'issued_date', 'inward_date', 'comments']
                if all(field in result['current_status'] for field in status_fields):
                    return True
                else:
                    self.log_test("Serial History Status Structure", False, f"Missing status fields: {result['current_status']}")
            else:
                self.log_test("Serial History Report Structure", False, f"Missing fields in response: {result}")
        return False

    def test_reports_serial_history_invalid(self):
        """Test GET /api/reports/serial-history/{serial_number} with invalid serial"""
        result = self.run_api_test(
            "Reports - Serial History Invalid Serial",
            "GET",
            "reports/serial-history/INVALID_SERIAL_123",
            404
        )
        return result is None  # Should return None for 404 status

    def test_reports_category_export(self):
        """Test GET /api/reports/category-export/{category_id} endpoint"""
        if not self.test_category_id:
            return False
            
        result = self.run_api_test(
            "Reports - Category Export Data",
            "GET",
            f"reports/category-export/{self.test_category_id}",
            200
        )
        
        if result:
            # Verify response structure
            required_fields = ['category', 'boards', 'issue_requests', 'bulk_issue_requests', 'statistics']
            if all(field in result for field in required_fields):
                # Verify statistics structure
                stats_fields = ['total_boards', 'in_stock', 'issued', 'repairing', 'total_requests', 'total_bulk_requests']
                if all(field in result['statistics'] for field in stats_fields):
                    return True
                else:
                    self.log_test("Category Export Statistics Structure", False, f"Missing stats fields: {result['statistics']}")
            else:
                self.log_test("Category Export Report Structure", False, f"Missing fields in response: {result}")
        return False

    def test_reports_category_export_invalid(self):
        """Test GET /api/reports/category-export/{category_id} with invalid category"""
        result = self.run_api_test(
            "Reports - Category Export Invalid Category",
            "GET",
            "reports/category-export/invalid-category-id",
            404
        )
        return result is None  # Should return None for 404 status

    def test_reports_serial_numbers_by_category(self):
        """Test GET /api/reports/serial-numbers/{category_id} endpoint - NEW FUNCTIONALITY"""
        if not self.test_category_id:
            return False
            
        result = self.run_api_test(
            "Reports - Serial Numbers by Category (NEW)",
            "GET",
            f"reports/serial-numbers/{self.test_category_id}",
            200
        )
        
        if result:
            # Verify response structure
            required_fields = ['category_id', 'category_name', 'serial_numbers']
            if all(field in result for field in required_fields):
                # Verify serial_numbers array structure
                if isinstance(result['serial_numbers'], list) and len(result['serial_numbers']) > 0:
                    serial_item = result['serial_numbers'][0]
                    serial_fields = ['serial_number', 'condition', 'location', 'status']
                    if all(field in serial_item for field in serial_fields):
                        # Verify status field format (should be "condition - location")
                        expected_status = f"{serial_item['condition']} - {serial_item['location']}"
                        if serial_item['status'] == expected_status:
                            return True
                        else:
                            self.log_test("Serial Numbers Status Format", False, 
                                        f"Expected status '{expected_status}', got '{serial_item['status']}'")
                    else:
                        self.log_test("Serial Numbers Item Structure", False, f"Missing fields in serial item: {serial_item}")
                else:
                    self.log_test("Serial Numbers Array", False, f"Empty or invalid serial_numbers array: {result['serial_numbers']}")
            else:
                self.log_test("Serial Numbers Response Structure", False, f"Missing fields in response: {result}")
        return False

    def test_reports_serial_numbers_by_category_invalid(self):
        """Test GET /api/reports/serial-numbers/{category_id} with invalid category - ERROR HANDLING"""
        result = self.run_api_test(
            "Reports - Serial Numbers Invalid Category (NEW)",
            "GET",
            "reports/serial-numbers/invalid-category-id-12345",
            404
        )
        return result is None  # Should return None for 404 status

    def test_reports_excel_export_low_stock(self):
        """Test GET /api/reports/export/low-stock Excel export endpoint - ENHANCED TESTING"""
        url = f"{self.api_url}/reports/export/low-stock"
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            success = response.status_code == 200
            if success:
                # Verify Content-Type header (EXCEL DOWNLOAD FIX)
                content_type = response.headers.get('Content-Type', '')
                expected_content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                if content_type != expected_content_type:
                    self.log_test("Low Stock Excel Content-Type", False, 
                                f"Expected '{expected_content_type}', got '{content_type}'")
                    return False
                
                # Verify Content-Disposition header (EXCEL DOWNLOAD FIX)
                content_disposition = response.headers.get('Content-Disposition', '')
                if not content_disposition.startswith('attachment; filename='):
                    self.log_test("Low Stock Excel Content-Disposition", False, 
                                f"Invalid Content-Disposition: '{content_disposition}'")
                    return False
                
                # Verify Access-Control-Expose-Headers for CORS (EXCEL DOWNLOAD FIX)
                expose_headers = response.headers.get('Access-Control-Expose-Headers', '')
                if 'Content-Disposition' not in expose_headers:
                    self.log_test("Low Stock Excel CORS Headers", False, 
                                f"Content-Disposition not exposed for CORS: '{expose_headers}'")
                    return False
                
                # Verify file size (should not be empty)
                content_length = len(response.content)
                if content_length < 1000:  # Excel files should be at least 1KB
                    self.log_test("Low Stock Excel File Size", False, 
                                f"File too small: {content_length} bytes")
                    return False
                
                self.log_test("Reports - Excel Export Low Stock (ENHANCED)", True, 
                            f"Excel file: {content_length} bytes, proper headers, CORS ready")
                return True
            else:
                self.log_test("Reports - Excel Export Low Stock", False, 
                            f"Status: {response.status_code}, Expected: 200")
                
        except Exception as e:
            self.log_test("Reports - Excel Export Low Stock", False, f"Exception: {str(e)}")
            
        return False

    def test_reports_excel_export_under_repair(self):
        """Test GET /api/reports/export/under-repair Excel export endpoint - ENHANCED TESTING"""
        url = f"{self.api_url}/reports/export/under-repair"
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            success = response.status_code == 200
            if success:
                # Verify Content-Type header (EXCEL DOWNLOAD FIX)
                content_type = response.headers.get('Content-Type', '')
                expected_content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                if content_type != expected_content_type:
                    self.log_test("Under Repair Excel Content-Type", False, 
                                f"Expected '{expected_content_type}', got '{content_type}'")
                    return False
                
                # Verify Content-Disposition header (EXCEL DOWNLOAD FIX)
                content_disposition = response.headers.get('Content-Disposition', '')
                if not content_disposition.startswith('attachment; filename='):
                    self.log_test("Under Repair Excel Content-Disposition", False, 
                                f"Invalid Content-Disposition: '{content_disposition}'")
                    return False
                
                # Verify Access-Control-Expose-Headers for CORS (EXCEL DOWNLOAD FIX)
                expose_headers = response.headers.get('Access-Control-Expose-Headers', '')
                if 'Content-Disposition' not in expose_headers:
                    self.log_test("Under Repair Excel CORS Headers", False, 
                                f"Content-Disposition not exposed for CORS: '{expose_headers}'")
                    return False
                
                # Verify file size (should not be empty)
                content_length = len(response.content)
                if content_length < 1000:  # Excel files should be at least 1KB
                    self.log_test("Under Repair Excel File Size", False, 
                                f"File too small: {content_length} bytes")
                    return False
                
                self.log_test("Reports - Excel Export Under Repair (ENHANCED)", True, 
                            f"Excel file: {content_length} bytes, proper headers, CORS ready")
                return True
            else:
                self.log_test("Reports - Excel Export Under Repair", False, 
                            f"Status: {response.status_code}, Expected: 200")
                
        except Exception as e:
            self.log_test("Reports - Excel Export Under Repair", False, f"Exception: {str(e)}")
            
        return False

    def test_reports_excel_export_serial_history(self):
        """Test GET /api/reports/export/serial-history/{serial_number} Excel export endpoint"""
        if not hasattr(self, 'test_serial_number'):
            return False
            
        url = f"{self.api_url}/reports/export/serial-history/{self.test_serial_number}"
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            success = response.status_code == 200
            if success:
                # Verify it's an Excel file
                content_type = response.headers.get('content-type', '')
                content_disposition = response.headers.get('content-disposition', '')
                
                is_excel = ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type or
                           'attachment' in content_disposition)
                
                if is_excel and len(response.content) > 0:
                    self.log_test("Reports - Excel Export Serial History", True, 
                                f"Excel file downloaded successfully, size: {len(response.content)} bytes")
                    return True
                else:
                    self.log_test("Reports - Excel Export Serial History", False, 
                                f"Invalid Excel response. Content-Type: {content_type}, Size: {len(response.content)}")
            else:
                self.log_test("Reports - Excel Export Serial History", False, 
                            f"Status: {response.status_code}, Expected: 200")
                
        except Exception as e:
            self.log_test("Reports - Excel Export Serial History", False, f"Exception: {str(e)}")
            
        return False

    def test_reports_excel_export_category(self):
        """Test GET /api/reports/export/category/{category_id} Excel export endpoint"""
        if not self.test_category_id:
            return False
            
        url = f"{self.api_url}/reports/export/category/{self.test_category_id}"
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            
            success = response.status_code == 200
            if success:
                # Verify it's an Excel file
                content_type = response.headers.get('content-type', '')
                content_disposition = response.headers.get('content-disposition', '')
                
                is_excel = ('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' in content_type or
                           'attachment' in content_disposition)
                
                if is_excel and len(response.content) > 0:
                    self.log_test("Reports - Excel Export Category", True, 
                                f"Excel file downloaded successfully, size: {len(response.content)} bytes")
                    return True
                else:
                    self.log_test("Reports - Excel Export Category", False, 
                                f"Invalid Excel response. Content-Type: {content_type}, Size: {len(response.content)}")
            else:
                self.log_test("Reports - Excel Export Category", False, 
                            f"Status: {response.status_code}, Expected: 200")
                
        except Exception as e:
            self.log_test("Reports - Excel Export Category", False, f"Exception: {str(e)}")
            
        return False

    def test_reports_permission_checks(self):
        """Test that reports endpoints require view_reports permission"""
        # Create a new user without view_reports permission
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"no_reports_user_{timestamp}@example.com"
        
        # Register new user
        register_result = self.run_api_test(
            "Reports Permission - Register User Without Permissions",
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
            
        # Save current token and switch to new user
        original_token = self.token
        self.token = register_result['access_token']
        
        # Test that reports endpoints return 403 for user without permissions
        endpoints_to_test = [
            "reports/low-stock",
            "reports/under-repair",
            f"reports/serial-history/{self.test_serial_number}" if hasattr(self, 'test_serial_number') else "reports/serial-history/TEST123",
            f"reports/category-export/{self.test_category_id}" if self.test_category_id else "reports/category-export/test-id"
        ]
        
        permission_tests_passed = 0
        for endpoint in endpoints_to_test:
            result = self.run_api_test(
                f"Reports Permission Check - {endpoint}",
                "GET",
                endpoint,
                403  # Should return 403 Forbidden
            )
            if result is None:  # 403 returns None in our test framework
                permission_tests_passed += 1
        
        # Test Excel export endpoints
        excel_endpoints = [
            "reports/export/low-stock",
            "reports/export/under-repair"
        ]
        
        for endpoint in excel_endpoints:
            result = self.run_api_test(
                f"Reports Excel Permission Check - {endpoint}",
                "GET",
                endpoint,
                403  # Should return 403 Forbidden
            )
            if result is None:  # 403 returns None in our test framework
                permission_tests_passed += 1
        
        # Restore original token
        self.token = original_token
        
        return permission_tests_passed == (len(endpoints_to_test) + len(excel_endpoints))

    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        if self.test_category_id:
            # Get all boards for this category and delete them
            boards_result = self.run_api_test(
                "Cleanup - Get Category Boards",
                "GET",
                "boards",
                200
            )
            
            if boards_result:
                category_boards = [board for board in boards_result if board.get('category_id') == self.test_category_id]
                for board in category_boards:
                    self.run_api_test(
                        f"Cleanup - Delete Board {board['id']}",
                        "DELETE",
                        f"boards/{board['id']}",
                        200
                    )
            
            # Delete the test category
            self.run_api_test(
                "Cleanup - Delete Test Category",
                "DELETE",
                f"categories/{self.test_category_id}",
                200
            )

    def run_reports_tests(self):
        """Run all reports functionality tests"""
        print("🔍 Starting Reports Functionality Testing...")
        print(f"📍 Testing against: {self.api_url}")
        print("=" * 80)
        
        # Login with provided credentials
        if not self.test_login_with_provided_credentials():
            print("❌ Login failed. Cannot proceed with reports testing.")
            return False
        
        # Setup test data
        if not self.setup_test_data():
            print("❌ Test data setup failed. Cannot proceed with reports testing.")
            return False
        
        print("\n🔍 REPORTS FUNCTIONALITY TESTING")
        print("=" * 50)
        
        # Test all reports endpoints
        self.test_reports_low_stock()
        self.test_reports_under_repair()
        self.test_reports_serial_history()
        self.test_reports_serial_history_invalid()
        self.test_reports_category_export()
        self.test_reports_category_export_invalid()
        
        # Test NEW serial numbers by category endpoint
        print("\n🆕 NEW FUNCTIONALITY TESTING")
        print("=" * 35)
        self.test_reports_serial_numbers_by_category()
        self.test_reports_serial_numbers_by_category_invalid()
        
        # Test Excel export endpoints
        print("\n📊 EXCEL EXPORT TESTING")
        print("=" * 30)
        self.test_reports_excel_export_low_stock()
        self.test_reports_excel_export_under_repair()
        self.test_reports_excel_export_serial_history()
        self.test_reports_excel_export_category()
        
        # Test permission checks
        print("\n🔒 PERMISSION TESTING")
        print("=" * 25)
        self.test_reports_permission_checks()
        
        # Clean up test data
        self.cleanup_test_data()
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 REPORTS TESTING SUMMARY")
        print("=" * 80)
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        print(f"🔢 Total Tests: {self.tests_run}")
        
        if self.tests_passed == self.tests_run:
            print("\n🎉 ALL REPORTS TESTS PASSED! 🎉")
        else:
            print(f"\n⚠️  {self.tests_run - self.tests_passed} test(s) failed. Check details above.")
            
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = ReportsAPITester()
    success = tester.run_reports_tests()
    sys.exit(0 if success else 1)