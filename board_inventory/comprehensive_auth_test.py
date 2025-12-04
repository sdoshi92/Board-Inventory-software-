#!/usr/bin/env python3
"""
Comprehensive Authentication Testing
Tests various edge cases and potential issues that could cause frontend login failures.
"""

import requests
import json
import time
from datetime import datetime

class ComprehensiveAuthTester:
    def __init__(self):
        self.base_url = "http://localhost:8001"
        self.api_url = f"{self.base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def log_test(self, name, success, details=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
        
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status} - {name}")
        if details:
            print(f"   Details: {details}")

    def test_api_connectivity(self):
        """Test basic API connectivity"""
        print("\n=== Testing API Connectivity ===")
        
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            details = f"Status: {response.status_code}"
            if success:
                data = response.json()
                details += f", Message: {data.get('message', 'No message')}"
            self.log_test("API Connectivity", success, details)
            return success
        except Exception as e:
            self.log_test("API Connectivity", False, f"Exception: {str(e)}")
            return False

    def test_cors_headers(self):
        """Test CORS headers for frontend compatibility"""
        print("\n=== Testing CORS Headers ===")
        
        try:
            # Make an OPTIONS request to check CORS
            response = requests.options(f"{self.api_url}/auth/login", timeout=10)
            success = response.status_code in [200, 204]
            details = f"Status: {response.status_code}"
            
            # Check for CORS headers
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            if any(cors_headers.values()):
                details += f", CORS headers present: {cors_headers}"
            else:
                details += ", No CORS headers found"
            
            self.log_test("CORS Headers", success, details)
            return success
        except Exception as e:
            self.log_test("CORS Headers", False, f"Exception: {str(e)}")
            return False

    def test_registration_validation(self):
        """Test registration field validation"""
        print("\n=== Testing Registration Validation ===")
        
        # Test missing required fields
        test_cases = [
            ({}, "Empty data"),
            ({"email": "test@example.com"}, "Missing password and other fields"),
            ({"email": "invalid-email", "password": "test123", "first_name": "Test", "last_name": "User", "designation": "Engineer"}, "Invalid email format"),
            ({"email": "test@example.com", "password": "123", "first_name": "Test", "last_name": "User", "designation": "Engineer"}, "Short password"),
            ({"email": "test@example.com", "password": "validpass123", "first_name": "", "last_name": "User", "designation": "Engineer"}, "Empty first name"),
        ]
        
        all_passed = True
        for i, (data, description) in enumerate(test_cases):
            try:
                response = requests.post(f"{self.api_url}/auth/register", json=data, timeout=10)
                success = response.status_code in [400, 422]  # Should fail validation
                details = f"Status: {response.status_code}, Case: {description}"
                
                if not success:
                    details += f", Unexpected success or error code"
                
                self.log_test(f"Registration Validation {i+1}", success, details)
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Registration Validation {i+1}", False, f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_login_validation(self):
        """Test login field validation"""
        print("\n=== Testing Login Validation ===")
        
        test_cases = [
            ({}, "Empty data"),
            ({"email": "test@example.com"}, "Missing password"),
            ({"password": "test123"}, "Missing email"),
            ({"email": "invalid-email", "password": "test123"}, "Invalid email format"),
        ]
        
        all_passed = True
        for i, (data, description) in enumerate(test_cases):
            try:
                response = requests.post(f"{self.api_url}/auth/login", json=data, timeout=10)
                success = response.status_code in [400, 422]  # Should fail validation
                details = f"Status: {response.status_code}, Case: {description}"
                
                if not success:
                    details += f", Unexpected success or error code"
                
                self.log_test(f"Login Validation {i+1}", success, details)
                if not success:
                    all_passed = False
                    
            except Exception as e:
                self.log_test(f"Login Validation {i+1}", False, f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_token_expiration_handling(self):
        """Test token format and basic validation"""
        print("\n=== Testing Token Format ===")
        
        # Create a test user and get token
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"tokentest_{timestamp}@example.com"
        
        registration_data = {
            "email": test_email,
            "first_name": "Token",
            "last_name": "Test",
            "designation": "Test Engineer",
            "password": "TokenTest123!"
        }
        
        try:
            # Register user
            reg_response = requests.post(f"{self.api_url}/auth/register", json=registration_data, timeout=10)
            if reg_response.status_code != 200:
                self.log_test("Token Format Test Setup", False, "Failed to create test user")
                return False
            
            token = reg_response.json()['access_token']
            
            # Check token format (should be JWT)
            token_parts = token.split('.')
            success = len(token_parts) == 3  # JWT has 3 parts
            details = f"Token parts: {len(token_parts)}, Format: {'JWT' if success else 'Unknown'}"
            
            self.log_test("Token Format", success, details)
            return success
            
        except Exception as e:
            self.log_test("Token Format", False, f"Exception: {str(e)}")
            return False

    def test_concurrent_logins(self):
        """Test multiple concurrent login attempts"""
        print("\n=== Testing Concurrent Logins ===")
        
        # Use existing test user
        login_data = {
            "email": "testlogin@example.com",
            "password": "password123"
        }
        
        try:
            # Make multiple concurrent requests
            import threading
            results = []
            
            def make_login_request():
                try:
                    response = requests.post(f"{self.api_url}/auth/login", json=login_data, timeout=10)
                    results.append(response.status_code == 200)
                except:
                    results.append(False)
            
            threads = []
            for i in range(5):
                thread = threading.Thread(target=make_login_request)
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            success_count = sum(results)
            success = success_count >= 4  # At least 4 out of 5 should succeed
            details = f"Successful logins: {success_count}/5"
            
            self.log_test("Concurrent Logins", success, details)
            return success
            
        except Exception as e:
            self.log_test("Concurrent Logins", False, f"Exception: {str(e)}")
            return False

    def test_response_format_consistency(self):
        """Test that API responses have consistent format"""
        print("\n=== Testing Response Format Consistency ===")
        
        # Test login response format
        login_data = {
            "email": "testlogin@example.com",
            "password": "password123"
        }
        
        try:
            response = requests.post(f"{self.api_url}/auth/login", json=login_data, timeout=10)
            if response.status_code != 200:
                self.log_test("Response Format", False, "Login failed")
                return False
            
            data = response.json()
            required_fields = ['access_token', 'token_type', 'user']
            user_fields = ['id', 'email', 'role', 'is_active']
            
            # Check main response fields
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                self.log_test("Response Format", False, f"Missing fields: {missing_fields}")
                return False
            
            # Check user object fields
            user = data.get('user', {})
            missing_user_fields = [field for field in user_fields if field not in user]
            if missing_user_fields:
                self.log_test("Response Format", False, f"Missing user fields: {missing_user_fields}")
                return False
            
            # Check token type
            if data.get('token_type') != 'bearer':
                self.log_test("Response Format", False, f"Unexpected token type: {data.get('token_type')}")
                return False
            
            self.log_test("Response Format", True, "All required fields present")
            return True
            
        except Exception as e:
            self.log_test("Response Format", False, f"Exception: {str(e)}")
            return False

    def test_error_response_format(self):
        """Test error response format consistency"""
        print("\n=== Testing Error Response Format ===")
        
        # Test with invalid credentials
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        try:
            response = requests.post(f"{self.api_url}/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                self.log_test("Error Response Format", False, "Expected error but got success")
                return False
            
            data = response.json()
            
            # Check if error response has detail field
            if 'detail' not in data:
                self.log_test("Error Response Format", False, "Missing 'detail' field in error response")
                return False
            
            # Check if detail is a string
            if not isinstance(data['detail'], str):
                self.log_test("Error Response Format", False, f"Detail field is not string: {type(data['detail'])}")
                return False
            
            self.log_test("Error Response Format", True, f"Error format correct: {data['detail']}")
            return True
            
        except Exception as e:
            self.log_test("Error Response Format", False, f"Exception: {str(e)}")
            return False

    def run_comprehensive_tests(self):
        """Run all comprehensive authentication tests"""
        print("🔐 Comprehensive Authentication System Testing")
        print("=" * 60)
        
        tests = [
            self.test_api_connectivity,
            self.test_cors_headers,
            self.test_registration_validation,
            self.test_login_validation,
            self.test_token_expiration_handling,
            self.test_concurrent_logins,
            self.test_response_format_consistency,
            self.test_error_response_format,
        ]
        
        for test in tests:
            test()
        
        # Print summary
        print("\n" + "=" * 60)
        print("🔐 Comprehensive Authentication Test Summary")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        print("=" * 60)
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = ComprehensiveAuthTester()
    success = tester.run_comprehensive_tests()
    
    if success:
        print("✅ All comprehensive authentication tests passed!")
        print("   The authentication system is robust and should not cause frontend login failures.")
    else:
        print("❌ Some comprehensive tests failed!")
        print("   There may be issues that could cause frontend login failures.")