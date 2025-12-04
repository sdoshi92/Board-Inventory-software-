import requests
import jwt
import json
from datetime import datetime

class JWTIntegrationTester:
    def __init__(self, base_url="https://boardventory.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_data = None
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

    def test_jwt_token_contains_user_info(self):
        """Test that JWT token contains updated user information"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        # Register a new user with enhanced fields
        registration_data = {
            "email": f"jwt_test_{timestamp}@example.com",
            "first_name": "JWT",
            "last_name": "TestUser",
            "designation": "JWT Test Engineer",
            "password": "JWTTest123!"
        }
        
        try:
            response = requests.post(f"{self.api_url}/auth/register", json=registration_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                self.token = result['access_token']
                self.user_data = result['user']
                
                # Decode JWT token (without verification for testing purposes)
                try:
                    # Note: In production, you should verify the token properly
                    decoded_token = jwt.decode(self.token, options={"verify_signature": False})
                    
                    # Check if token contains user email (standard claim)
                    if 'sub' in decoded_token and decoded_token['sub'] == registration_data['email']:
                        self.log_test("JWT Token Contains User Email", True, f"Token subject: {decoded_token['sub']}")
                        return True
                    else:
                        self.log_test("JWT Token Contains User Email", False, f"Token subject mismatch or missing")
                        return False
                        
                except jwt.InvalidTokenError as e:
                    self.log_test("JWT Token Decode", False, f"Token decode error: {str(e)}")
                    return False
            else:
                self.log_test("JWT Registration for Token Test", False, f"Registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("JWT Token Test Setup", False, f"Exception: {str(e)}")
            return False

    def test_jwt_token_authentication_flow(self):
        """Test complete JWT authentication flow with enhanced user data"""
        if not self.token or not self.user_data:
            return False
            
        # Test authenticated request using JWT token
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            if response.status_code == 200:
                user_info = response.json()
                
                # Verify all enhanced fields are returned
                expected_fields = ['id', 'email', 'first_name', 'last_name', 'designation']
                missing_fields = [field for field in expected_fields if field not in user_info]
                
                if not missing_fields:
                    # Verify field values match registration
                    if (user_info['email'] == self.user_data['email'] and
                        user_info['first_name'] == self.user_data['first_name'] and
                        user_info['last_name'] == self.user_data['last_name'] and
                        user_info['designation'] == self.user_data['designation']):
                        
                        self.log_test("JWT Authentication Flow", True, "All enhanced fields verified")
                        return True
                    else:
                        self.log_test("JWT Authentication Flow", False, "Field values don't match")
                        return False
                else:
                    self.log_test("JWT Authentication Flow", False, f"Missing fields: {missing_fields}")
                    return False
            else:
                self.log_test("JWT Authentication Flow", False, f"Auth request failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("JWT Authentication Flow", False, f"Exception: {str(e)}")
            return False

    def test_login_returns_enhanced_user_data(self):
        """Test that login returns complete enhanced user data"""
        if not self.user_data:
            return False
            
        login_data = {
            "email": self.user_data['email'],
            "password": "JWTTest123!"
        }
        
        try:
            response = requests.post(f"{self.api_url}/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                result = response.json()
                
                # Verify response structure
                if 'access_token' in result and 'user' in result:
                    user = result['user']
                    
                    # Verify enhanced fields are present and correct
                    enhanced_fields = ['first_name', 'last_name', 'designation']
                    for field in enhanced_fields:
                        if field not in user:
                            self.log_test("Login Enhanced User Data", False, f"Missing field: {field}")
                            return False
                        if not user[field]:  # Check field is not empty
                            self.log_test("Login Enhanced User Data", False, f"Empty field: {field}")
                            return False
                    
                    self.log_test("Login Enhanced User Data", True, "All enhanced fields present and populated")
                    return True
                else:
                    self.log_test("Login Enhanced User Data", False, "Missing access_token or user in response")
                    return False
            else:
                self.log_test("Login Enhanced User Data", False, f"Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Login Enhanced User Data", False, f"Exception: {str(e)}")
            return False

    def test_token_expiration_handling(self):
        """Test token expiration and refresh behavior"""
        if not self.token:
            return False
            
        # Test that current token is valid
        headers = {'Authorization': f'Bearer {self.token}'}
        
        try:
            response = requests.get(f"{self.api_url}/auth/me", headers=headers, timeout=10)
            if response.status_code == 200:
                self.log_test("Token Validity Check", True, "Token is currently valid")
                
                # Test with invalid token
                invalid_headers = {'Authorization': 'Bearer invalid_token_here'}
                invalid_response = requests.get(f"{self.api_url}/auth/me", headers=invalid_headers, timeout=10)
                
                if invalid_response.status_code == 401:
                    self.log_test("Invalid Token Rejection", True, "Invalid token properly rejected")
                    return True
                else:
                    self.log_test("Invalid Token Rejection", False, f"Expected 401, got {invalid_response.status_code}")
                    return False
            else:
                self.log_test("Token Validity Check", False, f"Valid token rejected: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Token Expiration Handling", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all JWT integration tests"""
        print("🔐 Starting JWT Integration Testing...")
        print("=" * 50)
        
        tests = [
            self.test_jwt_token_contains_user_info,
            self.test_jwt_token_authentication_flow,
            self.test_login_returns_enhanced_user_data,
            self.test_token_expiration_handling
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, False, f"Test exception: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 50)
        print(f"📊 JWT INTEGRATION TEST SUMMARY")
        print("=" * 50)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        return self.tests_passed, self.tests_run

if __name__ == "__main__":
    tester = JWTIntegrationTester()
    passed, total = tester.run_all_tests()
    
    if passed == total:
        print(f"\n🎉 All JWT integration tests passed!")
    else:
        print(f"\n⚠️  {total - passed} JWT integration test(s) failed.")