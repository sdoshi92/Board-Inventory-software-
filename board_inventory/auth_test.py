#!/usr/bin/env python3
"""
Authentication System Testing Script
Tests the authentication system of the electronics inventory management app.
"""

import requests
import json
import sys
from datetime import datetime

class AuthenticationTester:
    def __init__(self):
        # Use the backend URL from frontend .env
        self.base_url = "http://localhost:8001"
        self.api_url = f"{self.base_url}/api"
        self.token = None
        self.test_user_email = None
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

    def make_request(self, method, endpoint, data=None, headers=None, expected_status=None):
        """Make HTTP request and return response"""
        url = f"{self.api_url}/{endpoint}"
        request_headers = {'Content-Type': 'application/json'}
        
        if headers:
            request_headers.update(headers)

        try:
            if method == 'GET':
                response = requests.get(url, headers=request_headers, timeout=10)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=request_headers, timeout=10)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=request_headers, timeout=10)
            elif method == 'DELETE':
                response = requests.delete(url, headers=request_headers, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            return response

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def test_user_registration(self):
        """Test creating a new user with POST /api/auth/register"""
        print("\n=== Testing User Registration ===")
        
        # Generate unique test user
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"authtest_{timestamp}@example.com"
        test_password = "AuthTest123!"
        
        registration_data = {
            "email": test_email,
            "first_name": "Auth",
            "last_name": "Tester",
            "designation": "Test Engineer",
            "password": test_password
        }
        
        response = self.make_request('POST', 'auth/register', data=registration_data)
        
        if response is None:
            self.log_test("User Registration - Request", False, "Failed to make request")
            return False
        
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        
        if success:
            try:
                response_data = response.json()
                if 'access_token' in response_data and 'user' in response_data:
                    self.token = response_data['access_token']
                    self.test_user_email = test_email
                    self.test_password = test_password
                    details += f", Token received: {self.token[:20]}..."
                    self.log_test("User Registration", True, details)
                    return True
                else:
                    details += ", Missing access_token or user in response"
                    self.log_test("User Registration", False, details)
                    return False
            except json.JSONDecodeError:
                details += ", Invalid JSON response"
                self.log_test("User Registration", False, details)
                return False
        else:
            try:
                error_detail = response.json().get('detail', 'No error detail')
                details += f", Error: {error_detail}"
            except:
                details += f", Response: {response.text[:200]}"
            
            self.log_test("User Registration", False, details)
            return False

    def test_user_login_valid(self):
        """Test login with valid credentials using POST /api/auth/login"""
        print("\n=== Testing Valid User Login ===")
        
        if not self.test_user_email:
            self.log_test("User Login (Valid)", False, "No test user available")
            return False
        
        login_data = {
            "email": self.test_user_email,
            "password": self.test_password
        }
        
        response = self.make_request('POST', 'auth/login', data=login_data)
        
        if response is None:
            self.log_test("User Login (Valid) - Request", False, "Failed to make request")
            return False
        
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        
        if success:
            try:
                response_data = response.json()
                if 'access_token' in response_data and 'user' in response_data:
                    self.token = response_data['access_token']
                    details += f", Token received: {self.token[:20]}..."
                    self.log_test("User Login (Valid)", True, details)
                    return True
                else:
                    details += ", Missing access_token or user in response"
                    self.log_test("User Login (Valid)", False, details)
                    return False
            except json.JSONDecodeError:
                details += ", Invalid JSON response"
                self.log_test("User Login (Valid)", False, details)
                return False
        else:
            try:
                error_detail = response.json().get('detail', 'No error detail')
                details += f", Error: {error_detail}"
            except:
                details += f", Response: {response.text[:200]}"
            
            self.log_test("User Login (Valid)", False, details)
            return False

    def test_token_validation(self):
        """Test accessing a protected endpoint with the JWT token from login"""
        print("\n=== Testing Token Validation ===")
        
        if not self.token:
            self.log_test("Token Validation", False, "No token available")
            return False
        
        # Test accessing /api/auth/me endpoint which requires authentication
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.make_request('GET', 'auth/me', headers=headers)
        
        if response is None:
            self.log_test("Token Validation - Request", False, "Failed to make request")
            return False
        
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        
        if success:
            try:
                response_data = response.json()
                if 'email' in response_data and response_data['email'] == self.test_user_email:
                    details += f", User email verified: {response_data['email']}"
                    self.log_test("Token Validation", True, details)
                    return True
                else:
                    details += f", Unexpected user data: {response_data}"
                    self.log_test("Token Validation", False, details)
                    return False
            except json.JSONDecodeError:
                details += ", Invalid JSON response"
                self.log_test("Token Validation", False, details)
                return False
        else:
            try:
                error_detail = response.json().get('detail', 'No error detail')
                details += f", Error: {error_detail}"
            except:
                details += f", Response: {response.text[:200]}"
            
            self.log_test("Token Validation", False, details)
            return False

    def test_protected_endpoint_access(self):
        """Test accessing another protected endpoint to verify token works"""
        print("\n=== Testing Protected Endpoint Access ===")
        
        if not self.token:
            self.log_test("Protected Endpoint Access", False, "No token available")
            return False
        
        # Test accessing /api/categories endpoint which requires authentication
        headers = {'Authorization': f'Bearer {self.token}'}
        response = self.make_request('GET', 'categories', headers=headers)
        
        if response is None:
            self.log_test("Protected Endpoint Access - Request", False, "Failed to make request")
            return False
        
        # Categories endpoint might return 403 if user doesn't have view_categories permission
        # But it should not return 401 (unauthorized) if token is valid
        success = response.status_code in [200, 403]  # 200 = success, 403 = forbidden but authenticated
        details = f"Status: {response.status_code}"
        
        if success:
            if response.status_code == 200:
                details += ", Access granted to categories endpoint"
            elif response.status_code == 403:
                details += ", Access forbidden but token is valid (permission issue, not auth issue)"
            self.log_test("Protected Endpoint Access", True, details)
            return True
        else:
            try:
                error_detail = response.json().get('detail', 'No error detail')
                details += f", Error: {error_detail}"
            except:
                details += f", Response: {response.text[:200]}"
            
            self.log_test("Protected Endpoint Access", False, details)
            return False

    def test_invalid_login(self):
        """Test login with wrong credentials"""
        print("\n=== Testing Invalid Login ===")
        
        # Test with wrong email
        wrong_email_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = self.make_request('POST', 'auth/login', data=wrong_email_data)
        
        if response is None:
            self.log_test("Invalid Login (Wrong Email) - Request", False, "Failed to make request")
            return False
        
        success = response.status_code == 400  # Should return 400 for invalid credentials
        details = f"Status: {response.status_code}"
        
        if success:
            details += ", Correctly rejected invalid email"
            self.log_test("Invalid Login (Wrong Email)", True, details)
        else:
            try:
                error_detail = response.json().get('detail', 'No error detail')
                details += f", Error: {error_detail}"
            except:
                details += f", Response: {response.text[:200]}"
            self.log_test("Invalid Login (Wrong Email)", False, details)
            return False
        
        # Test with wrong password
        if self.test_user_email:
            wrong_password_data = {
                "email": self.test_user_email,
                "password": "wrongpassword123"
            }
            
            response = self.make_request('POST', 'auth/login', data=wrong_password_data)
            
            if response is None:
                self.log_test("Invalid Login (Wrong Password) - Request", False, "Failed to make request")
                return False
            
            success = response.status_code == 400  # Should return 400 for invalid credentials
            details = f"Status: {response.status_code}"
            
            if success:
                details += ", Correctly rejected invalid password"
                self.log_test("Invalid Login (Wrong Password)", True, details)
                return True
            else:
                try:
                    error_detail = response.json().get('detail', 'No error detail')
                    details += f", Error: {error_detail}"
                except:
                    details += f", Response: {response.text[:200]}"
                self.log_test("Invalid Login (Wrong Password)", False, details)
                return False
        
        return True

    def test_unauthorized_access(self):
        """Test accessing protected endpoint without token"""
        print("\n=== Testing Unauthorized Access ===")
        
        # Test accessing protected endpoint without Authorization header
        response = self.make_request('GET', 'auth/me')
        
        if response is None:
            self.log_test("Unauthorized Access - Request", False, "Failed to make request")
            return False
        
        success = response.status_code == 403  # FastAPI HTTPBearer returns 403 for missing token
        details = f"Status: {response.status_code}"
        
        if success:
            details += ", Correctly rejected request without token"
            self.log_test("Unauthorized Access", True, details)
            return True
        else:
            try:
                error_detail = response.json().get('detail', 'No error detail')
                details += f", Error: {error_detail}"
            except:
                details += f", Response: {response.text[:200]}"
            
            self.log_test("Unauthorized Access", False, details)
            return False

    def test_invalid_token(self):
        """Test accessing protected endpoint with invalid token"""
        print("\n=== Testing Invalid Token ===")
        
        # Test with malformed token
        headers = {'Authorization': 'Bearer invalid_token_here'}
        response = self.make_request('GET', 'auth/me', headers=headers)
        
        if response is None:
            self.log_test("Invalid Token - Request", False, "Failed to make request")
            return False
        
        success = response.status_code == 401  # Should return 401 for invalid token
        details = f"Status: {response.status_code}"
        
        if success:
            details += ", Correctly rejected invalid token"
            self.log_test("Invalid Token", True, details)
            return True
        else:
            try:
                error_detail = response.json().get('detail', 'No error detail')
                details += f", Error: {error_detail}"
            except:
                details += f", Response: {response.text[:200]}"
            
            self.log_test("Invalid Token", False, details)
            return False

    def test_existing_user_login(self):
        """Test login with the provided test credentials"""
        print("\n=== Testing Existing User Login ===")
        
        # Test with provided credentials
        login_data = {
            "email": "testlogin@example.com",
            "password": "password123"
        }
        
        response = self.make_request('POST', 'auth/login', data=login_data)
        
        if response is None:
            self.log_test("Existing User Login - Request", False, "Failed to make request")
            return False
        
        success = response.status_code == 200
        details = f"Status: {response.status_code}"
        
        if success:
            try:
                response_data = response.json()
                if 'access_token' in response_data and 'user' in response_data:
                    details += f", Successfully logged in existing user"
                    self.log_test("Existing User Login", True, details)
                    return True
                else:
                    details += ", Missing access_token or user in response"
                    self.log_test("Existing User Login", False, details)
                    return False
            except json.JSONDecodeError:
                details += ", Invalid JSON response"
                self.log_test("Existing User Login", False, details)
                return False
        else:
            try:
                error_detail = response.json().get('detail', 'No error detail')
                details += f", Error: {error_detail}"
                if response.status_code == 400 and "Incorrect email or password" in error_detail:
                    details += " (User may not exist - this is expected if user hasn't been created yet)"
            except:
                details += f", Response: {response.text[:200]}"
            
            self.log_test("Existing User Login", False, details)
            return False

    def run_all_tests(self):
        """Run all authentication tests"""
        print("🔐 Starting Authentication System Tests")
        print("=" * 50)
        
        # Test 1: User Registration
        registration_success = self.test_user_registration()
        
        # Test 2: User Login (with newly created user)
        login_success = self.test_user_login_valid()
        
        # Test 3: Token Validation
        token_validation_success = self.test_token_validation()
        
        # Test 4: Protected Endpoint Access
        protected_access_success = self.test_protected_endpoint_access()
        
        # Test 5: Invalid Login
        invalid_login_success = self.test_invalid_login()
        
        # Test 6: Unauthorized Access
        unauthorized_success = self.test_unauthorized_access()
        
        # Test 7: Invalid Token
        invalid_token_success = self.test_invalid_token()
        
        # Test 8: Existing User Login (with provided credentials)
        existing_user_success = self.test_existing_user_login()
        
        # Print summary
        print("\n" + "=" * 50)
        print("🔐 Authentication System Test Summary")
        print("=" * 50)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed / self.tests_run * 100):.1f}%")
        
        # Print failed tests
        failed_tests = [test for test in self.test_results if not test['success']]
        if failed_tests:
            print("\n❌ Failed Tests:")
            for test in failed_tests:
                print(f"  - {test['test_name']}: {test['details']}")
        
        print("\n" + "=" * 50)
        
        return self.tests_passed == self.tests_run

if __name__ == "__main__":
    tester = AuthenticationTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)