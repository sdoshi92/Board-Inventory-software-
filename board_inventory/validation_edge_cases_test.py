import requests
import json
from datetime import datetime

class ValidationEdgeCasesTester:
    def __init__(self, base_url="https://boardventory.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
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

    def test_registration_empty_string_fields(self):
        """Test registration with empty string fields"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        test_cases = [
            {
                "name": "Empty First Name",
                "data": {
                    "email": f"empty_fname_{timestamp}@example.com",
                    "first_name": "",  # Empty string
                    "last_name": "Doe",
                    "designation": "Engineer",
                    "password": "SecurePass123!"
                }
            },
            {
                "name": "Empty Last Name", 
                "data": {
                    "email": f"empty_lname_{timestamp}@example.com",
                    "first_name": "John",
                    "last_name": "",  # Empty string
                    "designation": "Engineer",
                    "password": "SecurePass123!"
                }
            },
            {
                "name": "Empty Designation",
                "data": {
                    "email": f"empty_designation_{timestamp}@example.com",
                    "first_name": "John",
                    "last_name": "Doe",
                    "designation": "",  # Empty string
                    "password": "SecurePass123!"
                }
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            try:
                response = requests.post(f"{self.api_url}/auth/register", json=test_case["data"], timeout=10)
                # Should fail with validation error
                if response.status_code in [400, 422]:
                    self.log_test(f"Empty String Validation - {test_case['name']}", True, f"Properly rejected empty string")
                else:
                    self.log_test(f"Empty String Validation - {test_case['name']}", False, f"Expected 400/422, got {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Empty String Validation - {test_case['name']}", False, f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_registration_whitespace_fields(self):
        """Test registration with whitespace-only fields"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        registration_data = {
            "email": f"whitespace_test_{timestamp}@example.com",
            "first_name": "   ",  # Whitespace only
            "last_name": "\t\n",  # Tabs and newlines
            "designation": "    ",  # Spaces only
            "password": "SecurePass123!"
        }
        
        try:
            response = requests.post(f"{self.api_url}/auth/register", json=registration_data, timeout=10)
            # Should either fail validation or trim whitespace
            if response.status_code in [400, 422]:
                self.log_test("Whitespace Fields Validation", True, "Whitespace-only fields properly rejected")
                return True
            elif response.status_code == 200:
                # If accepted, check if whitespace was trimmed
                result = response.json()
                user = result.get('user', {})
                if (user.get('first_name', '').strip() == '' or 
                    user.get('last_name', '').strip() == '' or 
                    user.get('designation', '').strip() == ''):
                    self.log_test("Whitespace Fields Validation", False, "Whitespace fields accepted without trimming")
                    return False
                else:
                    self.log_test("Whitespace Fields Validation", True, "Whitespace fields properly trimmed")
                    return True
            else:
                self.log_test("Whitespace Fields Validation", False, f"Unexpected status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Whitespace Fields Validation", False, f"Exception: {str(e)}")
            return False

    def test_registration_special_characters(self):
        """Test registration with special characters in names"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        test_cases = [
            {
                "name": "Names with Hyphens",
                "data": {
                    "email": f"hyphen_test_{timestamp}@example.com",
                    "first_name": "Mary-Jane",
                    "last_name": "Smith-Johnson",
                    "designation": "Senior Software Engineer",
                    "password": "SecurePass123!"
                },
                "should_pass": True
            },
            {
                "name": "Names with Apostrophes",
                "data": {
                    "email": f"apostrophe_test_{timestamp}@example.com",
                    "first_name": "O'Connor",
                    "last_name": "D'Angelo",
                    "designation": "Lead Engineer",
                    "password": "SecurePass123!"
                },
                "should_pass": True
            },
            {
                "name": "Names with Numbers",
                "data": {
                    "email": f"numbers_test_{timestamp}@example.com",
                    "first_name": "John123",
                    "last_name": "Doe456",
                    "designation": "Engineer Level 2",
                    "password": "SecurePass123!"
                },
                "should_pass": True  # Depends on business rules
            }
        ]
        
        all_passed = True
        for test_case in test_cases:
            try:
                response = requests.post(f"{self.api_url}/auth/register", json=test_case["data"], timeout=10)
                
                if test_case["should_pass"]:
                    if response.status_code == 200:
                        self.log_test(f"Special Characters - {test_case['name']}", True, "Accepted as expected")
                    else:
                        self.log_test(f"Special Characters - {test_case['name']}", False, f"Expected 200, got {response.status_code}")
                        all_passed = False
                else:
                    if response.status_code in [400, 422]:
                        self.log_test(f"Special Characters - {test_case['name']}", True, "Rejected as expected")
                    else:
                        self.log_test(f"Special Characters - {test_case['name']}", False, f"Expected 400/422, got {response.status_code}")
                        all_passed = False
                        
            except Exception as e:
                self.log_test(f"Special Characters - {test_case['name']}", False, f"Exception: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_registration_long_field_values(self):
        """Test registration with very long field values"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        # Test with extremely long values
        long_string = "A" * 1000  # 1000 characters
        
        registration_data = {
            "email": f"long_fields_{timestamp}@example.com",
            "first_name": long_string,
            "last_name": long_string,
            "designation": long_string,
            "password": "SecurePass123!"
        }
        
        try:
            response = requests.post(f"{self.api_url}/auth/register", json=registration_data, timeout=10)
            
            # Should either accept (if no length limits) or reject with validation error
            if response.status_code == 200:
                self.log_test("Long Field Values", True, "Long values accepted (no length limits)")
                return True
            elif response.status_code in [400, 422]:
                self.log_test("Long Field Values", True, "Long values properly rejected")
                return True
            else:
                self.log_test("Long Field Values", False, f"Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Long Field Values", False, f"Exception: {str(e)}")
            return False

    def test_registration_unicode_characters(self):
        """Test registration with Unicode characters"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        registration_data = {
            "email": f"unicode_test_{timestamp}@example.com",
            "first_name": "José",  # Accented characters
            "last_name": "Müller",  # Umlaut
            "designation": "Señior Engineer 工程师",  # Mixed Unicode
            "password": "SecurePass123!"
        }
        
        try:
            response = requests.post(f"{self.api_url}/auth/register", json=registration_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                user = result.get('user', {})
                
                # Verify Unicode characters are preserved
                if (user.get('first_name') == "José" and
                    user.get('last_name') == "Müller" and
                    "工程师" in user.get('designation', '')):
                    self.log_test("Unicode Characters", True, "Unicode characters properly preserved")
                    return True
                else:
                    self.log_test("Unicode Characters", False, "Unicode characters not preserved correctly")
                    return False
            else:
                self.log_test("Unicode Characters", False, f"Registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Unicode Characters", False, f"Exception: {str(e)}")
            return False

    def test_case_sensitivity_handling(self):
        """Test case sensitivity in email and other fields"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        # Register user with mixed case email
        registration_data = {
            "email": f"CaseSensitive_{timestamp}@Example.COM",
            "first_name": "Case",
            "last_name": "Sensitive",
            "designation": "Test Engineer",
            "password": "SecurePass123!"
        }
        
        try:
            response = requests.post(f"{self.api_url}/auth/register", json=registration_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                registered_email = result['user']['email']
                
                # Try to login with different case
                login_data = {
                    "email": registered_email.lower(),  # All lowercase
                    "password": "SecurePass123!"
                }
                
                login_response = requests.post(f"{self.api_url}/auth/login", json=login_data, timeout=10)
                
                if login_response.status_code == 200:
                    self.log_test("Case Sensitivity", True, "Email case insensitive login works")
                    return True
                else:
                    self.log_test("Case Sensitivity", False, f"Case insensitive login failed: {login_response.status_code}")
                    return False
            else:
                self.log_test("Case Sensitivity", False, f"Registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Case Sensitivity", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all validation edge case tests"""
        print("🧪 Starting Validation Edge Cases Testing...")
        print("=" * 55)
        
        tests = [
            self.test_registration_empty_string_fields,
            self.test_registration_whitespace_fields,
            self.test_registration_special_characters,
            self.test_registration_long_field_values,
            self.test_registration_unicode_characters,
            self.test_case_sensitivity_handling
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.log_test(test.__name__, False, f"Test exception: {str(e)}")
        
        # Print summary
        print("\n" + "=" * 55)
        print(f"📊 VALIDATION EDGE CASES TEST SUMMARY")
        print("=" * 55)
        print(f"Total Tests: {self.tests_run}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        return self.tests_passed, self.tests_run

if __name__ == "__main__":
    tester = ValidationEdgeCasesTester()
    passed, total = tester.run_all_tests()
    
    if passed == total:
        print(f"\n🎉 All validation edge case tests passed!")
    else:
        print(f"\n⚠️  {total - passed} validation test(s) failed.")