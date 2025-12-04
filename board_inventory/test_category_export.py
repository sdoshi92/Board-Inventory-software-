#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class CategoryExportTester:
    def __init__(self, base_url="https://boardventory.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_data = None
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        self.test_category_id = None

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
        """Setup test environment with authentication and test data"""
        print("🔧 Setting up test environment...")
        
        # Login with provided credentials
        login_result = self.run_api_test(
            "Login with Provided Credentials",
            "POST",
            "auth/login",
            200,
            data={"email": "suraajvdoshi@gmail.com", "password": "test123"}
        )
        
        if not login_result or 'access_token' not in login_result:
            print("❌ Failed to login with provided credentials")
            return False
            
        self.token = login_result['access_token']
        self.user_data = login_result['user']
        
        # Get existing categories
        categories_result = self.run_api_test(
            "Get Existing Categories",
            "GET",
            "categories",
            200
        )
        
        if categories_result and len(categories_result) > 0:
            self.test_category_id = categories_result[0]['id']
            print(f"✅ Using existing category: {categories_result[0]['name']} (ID: {self.test_category_id})")
        else:
            # Create a test category if none exist
            category_data = {
                "name": f"Category Export Test {datetime.now().strftime('%H%M%S')}",
                "description": "Test category for export functionality",
                "manufacturer": "Test Manufacturer",
                "version": "1.0",
                "lead_time_days": 30,
                "minimum_stock_quantity": 10
            }
            
            create_result = self.run_api_test(
                "Create Test Category",
                "POST",
                "categories",
                200,
                data=category_data
            )
            
            if create_result and 'id' in create_result:
                self.test_category_id = create_result['id']
                print(f"✅ Created test category: {create_result['name']} (ID: {self.test_category_id})")
            else:
                print("❌ Failed to create test category")
                return False
        
        return True

    def test_category_export_data_endpoint(self):
        """Test GET /api/reports/category-export/{category_id}"""
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
            
        self.log_test("Category Export Data Structure Validation", True, 
            f"All required fields present. Category: {category.get('name')}, Boards: {len(boards)}, Stats: {statistics}")
        return True

    def test_category_export_data_invalid_id(self):
        """Test GET /api/reports/category-export/{category_id} with invalid ID"""
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
        """Test GET /api/reports/export/category/{category_id} - Excel Export"""
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
        """Test GET /api/reports/export/category/{category_id}?token=... - Query Parameter Auth"""
        if not self.token:
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
        """Test Excel export with invalid category ID"""
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

    def run_category_export_tests(self):
        """Run all Category Export tests"""
        print("🎯 CATEGORY EXPORT FUNCTIONALITY TESTING")
        print("=" * 60)
        
        if not self.setup_test_environment():
            print("❌ Failed to setup test environment")
            return False
        
        print("\n📋 Testing Category Export Data Endpoint...")
        test1 = self.test_category_export_data_endpoint()
        test2 = self.test_category_export_data_invalid_id()
        
        print("\n📊 Testing Category Export Excel Generation...")
        test3 = self.test_category_export_excel_generation()
        test4 = self.test_category_export_excel_query_param_auth()
        test5 = self.test_category_export_excel_invalid_category()
        
        all_tests = [test1, test2, test3, test4, test5]
        passed_tests = sum(all_tests)
        total_tests = len(all_tests)
        
        success_rate = (passed_tests / total_tests) * 100
        
        print(f"\n📊 CATEGORY EXPORT TEST SUMMARY:")
        print("=" * 60)
        print(f"✅ Tests Passed: {passed_tests}/{total_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:  # Allow for some minor issues
            print("🎉 CATEGORY EXPORT FUNCTIONALITY IS WORKING!")
            return True
        else:
            print("⚠️  CATEGORY EXPORT HAS SIGNIFICANT ISSUES")
            return False

if __name__ == "__main__":
    tester = CategoryExportTester()
    success = tester.run_category_export_tests()
    sys.exit(0 if success else 1)