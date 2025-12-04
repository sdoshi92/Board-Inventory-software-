import requests
import sys
import json
from datetime import datetime

class EnhancedRegistrationTester:
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

    def test_enhanced_registration_with_all_fields(self):
        """Test enhanced user registration with all required fields"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        registration_data = {
            "email": f"enhanced_user_{timestamp}@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "designation": "Senior Electronics Engineer",
            "password": "SecurePass123!"
        }
        
        result = self.run_api_test(
            "Enhanced Registration - All Required Fields",
            "POST",
            "auth/register",
            200,
            data=registration_data
        )
        
        if result and 'access_token' in result and 'user' in result:
            self.token = result['access_token']
            self.user_data = result['user']
            
            # Verify user object contains all new fields
            user = result['user']
            expected_fields = ['id', 'email', 'first_name', 'last_name', 'designation', 'role', 'permissions', 'created_at', 'is_active']
            
            missing_fields = [field for field in expected_fields if field not in user]
            if missing_fields:
                self.log_test("Enhanced Registration - User Fields Validation", False, f"Missing fields: {missing_fields}")
                return False
            
            # Verify field values
            if (user['email'] == registration_data['email'] and
                user['first_name'] == registration_data['first_name'] and
                user['last_name'] == registration_data['last_name'] and
                user['designation'] == registration_data['designation']):
                
                # Verify password is not returned
                if 'password' not in user:
                    return True
                else:
                    self.log_test("Enhanced Registration - Password Security", False, "Password field returned in response")
                    return False
            else:
                self.log_test("Enhanced Registration - Field Values", False, f"Field values don't match input data")
                return False
        
        return False

    def test_registration_missing_first_name(self):
        """Test registration fails when first_name is missing"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        registration_data = {
            "email": f"missing_fname_{timestamp}@example.com",
            "last_name": "Doe",
            "designation": "Engineer",
            "password": "SecurePass123!"
            # Missing first_name
        }
        
        result = self.run_api_test(
            "Enhanced Registration - Missing First Name",
            "POST",
            "auth/register",
            422,  # Validation error
            data=registration_data
        )
        
        return result is None  # Should fail

    def test_registration_missing_last_name(self):
        """Test registration fails when last_name is missing"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        registration_data = {
            "email": f"missing_lname_{timestamp}@example.com",
            "first_name": "John",
            "designation": "Engineer",
            "password": "SecurePass123!"
            # Missing last_name
        }
        
        result = self.run_api_test(
            "Enhanced Registration - Missing Last Name",
            "POST",
            "auth/register",
            422,  # Validation error
            data=registration_data
        )
        
        return result is None  # Should fail

    def test_registration_missing_designation(self):
        """Test registration fails when designation is missing"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        registration_data = {
            "email": f"missing_designation_{timestamp}@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "SecurePass123!"
            # Missing designation
        }
        
        result = self.run_api_test(
            "Enhanced Registration - Missing Designation",
            "POST",
            "auth/register",
            422,  # Validation error
            data=registration_data
        )
        
        return result is None  # Should fail

    def test_registration_missing_email(self):
        """Test registration fails when email is missing"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        registration_data = {
            "first_name": "John",
            "last_name": "Doe",
            "designation": "Engineer",
            "password": "SecurePass123!"
            # Missing email
        }
        
        result = self.run_api_test(
            "Enhanced Registration - Missing Email",
            "POST",
            "auth/register",
            422,  # Validation error
            data=registration_data
        )
        
        return result is None  # Should fail

    def test_registration_missing_password(self):
        """Test registration fails when password is missing"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        registration_data = {
            "email": f"missing_password_{timestamp}@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "designation": "Engineer"
            # Missing password
        }
        
        result = self.run_api_test(
            "Enhanced Registration - Missing Password",
            "POST",
            "auth/register",
            422,  # Validation error
            data=registration_data
        )
        
        return result is None  # Should fail

    def test_registration_invalid_email_format(self):
        """Test registration fails with invalid email format"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        registration_data = {
            "email": f"invalid_email_{timestamp}",  # Missing @ and domain
            "first_name": "John",
            "last_name": "Doe",
            "designation": "Engineer",
            "password": "SecurePass123!"
        }
        
        result = self.run_api_test(
            "Enhanced Registration - Invalid Email Format",
            "POST",
            "auth/register",
            422,  # Validation error
            data=registration_data
        )
        
        return result is None  # Should fail

    def test_registration_weak_password(self):
        """Test registration fails with weak password"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        registration_data = {
            "email": f"weak_password_{timestamp}@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "designation": "Engineer",
            "password": "123"  # Too short
        }
        
        result = self.run_api_test(
            "Enhanced Registration - Weak Password",
            "POST",
            "auth/register",
            400,  # Bad request
            data=registration_data
        )
        
        return result is None  # Should fail

    def test_registration_duplicate_email(self):
        """Test registration fails with duplicate email"""
        if not self.user_data:
            return False
            
        # Try to register with same email as previously registered user
        registration_data = {
            "email": self.user_data['email'],  # Duplicate email
            "first_name": "Jane",
            "last_name": "Smith",
            "designation": "Junior Engineer",
            "password": "AnotherPass123!"
        }
        
        result = self.run_api_test(
            "Enhanced Registration - Duplicate Email",
            "POST",
            "auth/register",
            400,  # Bad request
            data=registration_data
        )
        
        return result is None  # Should fail

    def test_login_with_enhanced_user(self):
        """Test login with enhanced user credentials"""
        if not self.user_data:
            return False
            
        # Get the password from the original registration (we need to store it)
        # For this test, we'll use the password from the first successful registration
        login_data = {
            "email": self.user_data['email'],
            "password": "SecurePass123!"  # Password from first registration
        }
        
        result = self.run_api_test(
            "Enhanced Registration - Login with Enhanced User",
            "POST",
            "auth/login",
            200,
            data=login_data
        )
        
        if result and 'access_token' in result and 'user' in result:
            # Verify JWT token includes updated user information
            user = result['user']
            if (user['first_name'] and user['last_name'] and user['designation'] and
                user['email'] == self.user_data['email']):
                return True
            else:
                self.log_test("Enhanced Registration - Login User Data", False, "User data incomplete in login response")
        
        return False

    def test_get_current_user_enhanced(self):
        """Test getting current user info with enhanced fields"""
        if not self.token:
            return False
            
        result = self.run_api_test(
            "Enhanced Registration - Get Current User",
            "GET",
            "auth/me",
            200
        )
        
        if result:
            # Verify all enhanced fields are present
            expected_fields = ['id', 'email', 'first_name', 'last_name', 'designation', 'role', 'permissions', 'created_at', 'is_active']
            missing_fields = [field for field in expected_fields if field not in result]
            
            if not missing_fields:
                # Verify field values are not empty
                if (result['first_name'] and result['last_name'] and result['designation']):
                    return True
                else:
                    self.log_test("Enhanced Registration - Current User Field Values", False, "Some enhanced fields are empty")
            else:
                self.log_test("Enhanced Registration - Current User Fields", False, f"Missing fields: {missing_fields}")
        
        return False

    def test_user_model_backward_compatibility(self):
        """Test that User model works with existing user records"""
        # This test verifies that the enhanced User model can handle existing records
        # We'll test by getting all users (if admin) or current user
        
        if not self.token:
            return False
            
        # Test getting current user (should work for any user)
        result = self.run_api_test(
            "Enhanced Registration - Backward Compatibility Test",
            "GET",
            "auth/me",
            200
        )
        
        if result:
            # Verify the response has the expected structure
            # Even if some fields might be None for older records, they should be present
            required_fields = ['id', 'email', 'role', 'created_at', 'is_active']
            enhanced_fields = ['first_name', 'last_name', 'designation']
            
            # Check required fields are present
            missing_required = [field for field in required_fields if field not in result]
            if missing_required:
                self.log_test("Enhanced Registration - Backward Compatibility Required Fields", False, f"Missing required fields: {missing_required}")
                return False
            
            # Check enhanced fields are present (can be None for older records)
            missing_enhanced = [field for field in enhanced_fields if field not in result]
            if missing_enhanced:
                self.log_test("Enhanced Registration - Backward Compatibility Enhanced Fields", False, f"Missing enhanced fields: {missing_enhanced}")
                return False
            
            return True
        
        return False

    def test_user_update_model_with_new_fields(self):
        """Test UserUpdate model with new fields"""
        if not self.token or not self.user_data:
            return False
            
        # First, make current user admin to test user updates
        admin_result = self.run_api_test(
            "Enhanced Registration - Setup Admin for Update Test",
            "POST",
            f"setup-admin?email={self.user_data['email']}",
            200
        )
        
        if not admin_result:
            return False
            
        # Test updating user with new fields
        update_data = {
            "first_name": "UpdatedJohn",
            "last_name": "UpdatedDoe",
            "designation": "Lead Electronics Engineer"
        }
        
        result = self.run_api_test(
            "Enhanced Registration - Update User with New Fields",
            "PUT",
            f"users/{self.user_data['email']}",
            200,
            data=update_data
        )
        
        if result:
            # Verify the updated fields
            if (result['first_name'] == update_data['first_name'] and
                result['last_name'] == update_data['last_name'] and
                result['designation'] == update_data['designation']):
                return True
            else:
                self.log_test("Enhanced Registration - User Update Verification", False, "Updated fields don't match expected values")
        
        return False

    def test_database_storage_verification(self):
        """Test that user record includes all new fields in database"""
        if not self.token:
            return False
            
        # Get current user to verify database storage
        result = self.run_api_test(
            "Enhanced Registration - Database Storage Verification",
            "GET",
            "auth/me",
            200
        )
        
        if result:
            # Verify all fields are properly stored and retrieved
            expected_structure = {
                'id': str,
                'email': str,
                'first_name': str,
                'last_name': str,
                'designation': str,
                'role': str,
                'permissions': list,
                'created_at': str,
                'is_active': bool
            }
            
            for field, expected_type in expected_structure.items():
                if field not in result:
                    self.log_test("Enhanced Registration - Database Field Missing", False, f"Field '{field}' missing from database record")
                    return False
                
                if not isinstance(result[field], expected_type):
                    self.log_test("Enhanced Registration - Database Field Type", False, f"Field '{field}' has wrong type. Expected {expected_type}, got {type(result[field])}")
                    return False
            
            return True
        
        return False

    def test_registration_response_structure(self):
        """Test that registration response has correct structure"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        registration_data = {
            "email": f"response_test_{timestamp}@example.com",
            "first_name": "Response",
            "last_name": "Test",
            "designation": "Test Engineer",
            "password": "ResponseTest123!"
        }
        
        result = self.run_api_test(
            "Enhanced Registration - Response Structure Test",
            "POST",
            "auth/register",
            200,
            data=registration_data
        )
        
        if result:
            # Verify response structure
            expected_top_level = ['access_token', 'token_type', 'user']
            missing_top_level = [field for field in expected_top_level if field not in result]
            
            if missing_top_level:
                self.log_test("Enhanced Registration - Response Top Level", False, f"Missing top-level fields: {missing_top_level}")
                return False
            
            # Verify token type
            if result['token_type'] != 'bearer':
                self.log_test("Enhanced Registration - Token Type", False, f"Expected token_type 'bearer', got '{result['token_type']}'")
                return False
            
            # Verify user object structure
            user = result['user']
            expected_user_fields = ['id', 'email', 'first_name', 'last_name', 'designation', 'role', 'permissions', 'created_at', 'is_active']
            missing_user_fields = [field for field in expected_user_fields if field not in user]
            
            if missing_user_fields:
                self.log_test("Enhanced Registration - Response User Fields", False, f"Missing user fields: {missing_user_fields}")
                return False
            
            # Verify sensitive data is not included
            if 'password' in user:
                self.log_test("Enhanced Registration - Response Security", False, "Password field included in response")
                return False
            
            return True
        
        return False

    def run_all_tests(self):
        """Run all enhanced registration tests"""
        print("🚀 Starting Enhanced User Registration Testing...")
        print("=" * 60)
        
        # Test enhanced registration functionality
        tests = [
            self.test_enhanced_registration_with_all_fields,
            self.test_registration_missing_first_name,
            self.test_registration_missing_last_name,
            self.test_registration_missing_designation,
            self.test_registration_missing_email,
            self.test_registration_missing_password,
            self.test_registration_invalid_email_format,
            self.test_registration_weak_password,
            self.test_registration_duplicate_email,
            self.test_login_with_enhanced_user,
            self.test_get_current_user_enhanced,
            self.test_user_model_backward_compatibility,
            self.test_user_update_model_with_new_fields,
            self.test_database_storage_verification,
            self.test_registration_response_structure
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, False, f"Test exception: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 ENHANCED REGISTRATION TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if self.tests_run - self.tests_passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  - {result['test_name']}: {result['details']}")
        
        return self.tests_passed, self.tests_run

if __name__ == "__main__":
    tester = EnhancedRegistrationTester()
    passed, total = tester.run_all_tests()
    
    if passed == total:
        print(f"\n🎉 All tests passed! Enhanced user registration functionality is working correctly.")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Enhanced user registration needs attention.")
        sys.exit(1)