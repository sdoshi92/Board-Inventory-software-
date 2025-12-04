import requests
import sys
import json
from datetime import datetime

class PermissionSystemTester:
    def __init__(self, base_url="https://boardventory.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.admin_token = None
        self.user_token = None
        self.admin_user_data = None
        self.regular_user_data = None
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

    def run_api_test(self, name, method, endpoint, expected_status, data=None, headers=None, token=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        test_headers = {'Content-Type': 'application/json'}
        
        # Use specific token if provided, otherwise use admin token
        if token:
            test_headers['Authorization'] = f'Bearer {token}'
        elif self.admin_token:
            test_headers['Authorization'] = f'Bearer {self.admin_token}'
        
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

    def setup_test_users(self):
        """Create admin and regular users for testing"""
        timestamp = datetime.now().strftime('%H%M%S')
        
        # Create admin user
        admin_email = f"admin_user_{timestamp}@example.com"
        admin_data = {
            "email": admin_email,
            "first_name": "Admin",
            "last_name": "User",
            "designation": "System Administrator",
            "password": "AdminPass123!"
        }
        
        admin_result = self.run_api_test(
            "Setup - Create Admin User",
            "POST",
            "auth/register",
            200,
            data=admin_data,
            token=""  # No token for registration
        )
        
        if not admin_result or 'access_token' not in admin_result:
            return False
            
        self.admin_token = admin_result['access_token']
        self.admin_user_data = admin_result['user']
        
        # Make user admin
        setup_result = self.run_api_test(
            "Setup - Make User Admin",
            "POST",
            f"setup-admin?email={admin_email}",
            200
        )
        
        if not setup_result:
            return False
        
        # Create regular user
        user_email = f"regular_user_{timestamp}@example.com"
        user_data = {
            "email": user_email,
            "first_name": "Regular",
            "last_name": "User", 
            "designation": "Engineer",
            "password": "UserPass123!"
        }
        
        user_result = self.run_api_test(
            "Setup - Create Regular User",
            "POST",
            "auth/register",
            200,
            data=user_data,
            token=""  # No token for registration
        )
        
        if not user_result or 'access_token' not in user_result:
            return False
            
        self.user_token = user_result['access_token']
        self.regular_user_data = user_result['user']
        
        return True

    def test_get_available_permissions(self):
        """Test GET /api/permissions/available returns complete permission list"""
        # Test with admin user
        result = self.run_api_test(
            "Get Available Permissions - Admin Access",
            "GET",
            "permissions/available",
            200,
            token=self.admin_token
        )
        
        if not result or 'permissions' not in result:
            return False
            
        permissions = result['permissions']
        expected_permissions = [
            "view_dashboard", "view_categories", "create_categories", "edit_categories",
            "view_boards", "create_boards", "edit_boards", "view_inward", "create_inward",
            "view_search", "view_issue_requests", "create_issue_requests", 
            "approve_issue_requests", "view_outward", "create_outward",
            "view_user_management", "manage_users"
        ]
        
        # Check if all expected permissions are present
        missing_permissions = [p for p in expected_permissions if p not in permissions]
        if missing_permissions:
            self.log_test("Available Permissions Completeness", False, 
                f"Missing permissions: {missing_permissions}")
            return False
            
        # Test with regular user (should get 403)
        self.run_api_test(
            "Get Available Permissions - Regular User Access (Should Fail)",
            "GET",
            "permissions/available",
            403,
            token=self.user_token
        )
        
        return True

    def test_get_user_permissions(self):
        """Test GET /api/users/me/permissions returns user's effective permissions"""
        # Test admin user permissions
        admin_result = self.run_api_test(
            "Get User Permissions - Admin User",
            "GET",
            "users/me/permissions",
            200,
            token=self.admin_token
        )
        
        if not admin_result or 'permissions' not in admin_result:
            return False
            
        admin_permissions = admin_result['permissions']
        
        # Admin should have all permissions
        expected_admin_permissions = [
            "view_dashboard", "view_categories", "create_categories", "edit_categories",
            "view_boards", "create_boards", "edit_boards", "view_inward", "create_inward",
            "view_search", "view_issue_requests", "create_issue_requests", 
            "approve_issue_requests", "view_outward", "create_outward",
            "view_user_management", "manage_users"
        ]
        
        missing_admin_permissions = [p for p in expected_admin_permissions if p not in admin_permissions]
        if missing_admin_permissions:
            self.log_test("Admin User Permissions Completeness", False, 
                f"Admin missing permissions: {missing_admin_permissions}")
            return False
        
        # Test regular user permissions
        user_result = self.run_api_test(
            "Get User Permissions - Regular User",
            "GET",
            "users/me/permissions",
            200,
            token=self.user_token
        )
        
        if not user_result or 'permissions' not in user_result:
            return False
            
        user_permissions = user_result['permissions']
        
        # Regular user should have empty permissions by default
        if len(user_permissions) != 0:
            self.log_test("Regular User Default Permissions", False, 
                f"Regular user should have no permissions by default, got: {user_permissions}")
            return False
            
        return True

    def test_admin_password_reset(self):
        """Test POST /api/users/reset-password for admin password reset functionality"""
        if not self.regular_user_data:
            return False
            
        # Test admin can reset user password
        reset_data = {
            "user_id": self.regular_user_data['id'],
            "new_password": "NewPassword123!"
        }
        
        reset_result = self.run_api_test(
            "Admin Password Reset - Valid Request",
            "POST",
            "users/reset-password",
            200,
            data=reset_data,
            token=self.admin_token
        )
        
        if not reset_result or 'message' not in reset_result:
            return False
        
        # Test regular user cannot reset passwords
        self.run_api_test(
            "Admin Password Reset - Regular User Access (Should Fail)",
            "POST",
            "users/reset-password",
            403,
            data=reset_data,
            token=self.user_token
        )
        
        # Test password length validation
        invalid_reset_data = {
            "user_id": self.regular_user_data['id'],
            "new_password": "123"  # Too short
        }
        
        self.run_api_test(
            "Admin Password Reset - Invalid Password Length",
            "POST",
            "users/reset-password",
            422,
            data=invalid_reset_data,
            token=self.admin_token
        )
        
        # Test non-existent user
        nonexistent_reset_data = {
            "user_id": "nonexistent-user-id",
            "new_password": "ValidPassword123!"
        }
        
        self.run_api_test(
            "Admin Password Reset - Non-existent User",
            "POST",
            "users/reset-password",
            404,
            data=nonexistent_reset_data,
            token=self.admin_token
        )
        
        return True

    def test_admin_user_deletion(self):
        """Test DELETE /api/users/{user_id} for admin user deletion"""
        # Create a test user to delete
        timestamp = datetime.now().strftime('%H%M%S')
        delete_user_data = {
            "email": f"delete_test_{timestamp}@example.com",
            "first_name": "Delete",
            "last_name": "Test",
            "designation": "Test User",
            "password": "DeleteTest123!"
        }
        
        create_result = self.run_api_test(
            "User Deletion - Create Test User",
            "POST",
            "auth/register",
            200,
            data=delete_user_data,
            token=""
        )
        
        if not create_result or 'user' not in create_result:
            return False
            
        test_user_id = create_result['user']['id']
        
        # Test admin can delete user
        delete_result = self.run_api_test(
            "Admin User Deletion - Valid Request",
            "DELETE",
            f"users/{test_user_id}",
            200,
            token=self.admin_token
        )
        
        if not delete_result or 'message' not in delete_result:
            return False
        
        # Test regular user cannot delete users
        self.run_api_test(
            "Admin User Deletion - Regular User Access (Should Fail)",
            "DELETE",
            f"users/{test_user_id}",
            403,
            token=self.user_token
        )
        
        # Test admin cannot delete their own account
        self.run_api_test(
            "Admin User Deletion - Self Deletion (Should Fail)",
            "DELETE",
            f"users/{self.admin_user_data['id']}",
            400,
            token=self.admin_token
        )
        
        # Test deleting non-existent user
        self.run_api_test(
            "Admin User Deletion - Non-existent User",
            "DELETE",
            "users/nonexistent-user-id",
            404,
            token=self.admin_token
        )
        
        return True

    def test_admin_permission_management(self):
        """Test PUT /api/users/{user_id}/permissions for permission management"""
        if not self.regular_user_data:
            return False
            
        # Test admin can update user permissions
        permission_data = {
            "user_id": self.regular_user_data['id'],
            "permissions": ["view_dashboard", "view_categories", "view_boards"]
        }
        
        update_result = self.run_api_test(
            "Admin Permission Management - Valid Update",
            "PUT",
            f"users/{self.regular_user_data['id']}/permissions",
            200,
            data=permission_data,
            token=self.admin_token
        )
        
        if not update_result or 'message' not in update_result:
            return False
        
        # Verify permissions were updated
        verify_result = self.run_api_test(
            "Admin Permission Management - Verify Update",
            "GET",
            "users/me/permissions",
            200,
            token=self.user_token
        )
        
        if not verify_result or 'permissions' not in verify_result:
            return False
            
        updated_permissions = verify_result['permissions']
        expected_permissions = ["view_dashboard", "view_categories", "view_boards"]
        
        if set(updated_permissions) != set(expected_permissions):
            self.log_test("Permission Update Verification", False, 
                f"Expected {expected_permissions}, got {updated_permissions}")
            return False
        
        # Test regular user cannot update permissions
        self.run_api_test(
            "Admin Permission Management - Regular User Access (Should Fail)",
            "PUT",
            f"users/{self.regular_user_data['id']}/permissions",
            403,
            data=permission_data,
            token=self.user_token
        )
        
        # Test invalid permissions
        invalid_permission_data = {
            "user_id": self.regular_user_data['id'],
            "permissions": ["invalid_permission", "another_invalid"]
        }
        
        self.run_api_test(
            "Admin Permission Management - Invalid Permissions",
            "PUT",
            f"users/{self.regular_user_data['id']}/permissions",
            400,
            data=invalid_permission_data,
            token=self.admin_token
        )
        
        return True

    def test_permission_based_access_control(self):
        """Test protected endpoints with permission checks"""
        # First, remove all permissions from regular user
        clear_permissions_data = {
            "user_id": self.regular_user_data['id'],
            "permissions": []
        }
        
        self.run_api_test(
            "Permission Access Control - Clear User Permissions",
            "PUT",
            f"users/{self.regular_user_data['id']}/permissions",
            200,
            data=clear_permissions_data,
            token=self.admin_token
        )
        
        # Test dashboard access without permission
        self.run_api_test(
            "Permission Access Control - Dashboard Without Permission",
            "GET",
            "dashboard/stats",
            403,
            token=self.user_token
        )
        
        # Test categories access without permission
        self.run_api_test(
            "Permission Access Control - Categories Without Permission",
            "GET",
            "categories",
            403,
            token=self.user_token
        )
        
        # Test issue requests access without permission
        self.run_api_test(
            "Permission Access Control - Issue Requests Without Permission",
            "GET",
            "issue-requests",
            403,
            token=self.user_token
        )
        
        # Grant specific permissions and test access
        grant_permissions_data = {
            "user_id": self.regular_user_data['id'],
            "permissions": ["view_dashboard", "view_categories", "view_issue_requests"]
        }
        
        self.run_api_test(
            "Permission Access Control - Grant Specific Permissions",
            "PUT",
            f"users/{self.regular_user_data['id']}/permissions",
            200,
            data=grant_permissions_data,
            token=self.admin_token
        )
        
        # Test dashboard access with permission
        dashboard_result = self.run_api_test(
            "Permission Access Control - Dashboard With Permission",
            "GET",
            "dashboard/stats",
            200,
            token=self.user_token
        )
        
        # Test categories access with permission
        categories_result = self.run_api_test(
            "Permission Access Control - Categories With Permission",
            "GET",
            "categories",
            200,
            token=self.user_token
        )
        
        # Test issue requests access with permission
        requests_result = self.run_api_test(
            "Permission Access Control - Issue Requests With Permission",
            "GET",
            "issue-requests",
            200,
            token=self.user_token
        )
        
        # Test admin user can access all endpoints regardless of permissions
        admin_dashboard = self.run_api_test(
            "Permission Access Control - Admin Dashboard Access",
            "GET",
            "dashboard/stats",
            200,
            token=self.admin_token
        )
        
        admin_categories = self.run_api_test(
            "Permission Access Control - Admin Categories Access",
            "GET",
            "categories",
            200,
            token=self.admin_token
        )
        
        admin_requests = self.run_api_test(
            "Permission Access Control - Admin Issue Requests Access",
            "GET",
            "issue-requests",
            200,
            token=self.admin_token
        )
        
        return (dashboard_result is not None and categories_result is not None and 
                requests_result is not None and admin_dashboard is not None and 
                admin_categories is not None and admin_requests is not None)

    def test_user_creation_default_permissions(self):
        """Test new user registration creates users with no default permissions"""
        timestamp = datetime.now().strftime('%H%M%S')
        new_user_data = {
            "email": f"new_user_{timestamp}@example.com",
            "first_name": "New",
            "last_name": "User",
            "designation": "Test Engineer",
            "password": "NewUser123!"
        }
        
        # Create new user
        create_result = self.run_api_test(
            "User Creation - Register New User",
            "POST",
            "auth/register",
            200,
            data=new_user_data,
            token=""
        )
        
        if not create_result or 'access_token' not in create_result:
            return False
            
        new_user_token = create_result['access_token']
        new_user_info = create_result['user']
        
        # Check user has no default permissions
        permissions_result = self.run_api_test(
            "User Creation - Check Default Permissions",
            "GET",
            "users/me/permissions",
            200,
            token=new_user_token
        )
        
        if not permissions_result or 'permissions' not in permissions_result:
            return False
            
        default_permissions = permissions_result['permissions']
        if len(default_permissions) != 0:
            self.log_test("User Creation Default Permissions", False, 
                f"New user should have no permissions, got: {default_permissions}")
            return False
        
        # Verify new user cannot access protected resources
        self.run_api_test(
            "User Creation - Protected Resource Access (Should Fail)",
            "GET",
            "dashboard/stats",
            403,
            token=new_user_token
        )
        
        self.run_api_test(
            "User Creation - Categories Access (Should Fail)",
            "GET",
            "categories",
            403,
            token=new_user_token
        )
        
        # Test admin role assignment gives full access
        # Make new user admin
        admin_setup_result = self.run_api_test(
            "User Creation - Make User Admin",
            "POST",
            f"setup-admin?email={new_user_data['email']}",
            200,
            token=self.admin_token
        )
        
        if not admin_setup_result:
            return False
        
        # Check admin user now has all permissions
        admin_permissions_result = self.run_api_test(
            "User Creation - Check Admin Permissions",
            "GET",
            "users/me/permissions",
            200,
            token=new_user_token
        )
        
        if not admin_permissions_result or 'permissions' not in admin_permissions_result:
            return False
            
        admin_permissions = admin_permissions_result['permissions']
        expected_admin_permissions = [
            "view_dashboard", "view_categories", "create_categories", "edit_categories",
            "view_boards", "create_boards", "edit_boards", "view_inward", "create_inward",
            "view_search", "view_issue_requests", "create_issue_requests", 
            "approve_issue_requests", "view_outward", "create_outward",
            "view_user_management", "manage_users"
        ]
        
        missing_permissions = [p for p in expected_admin_permissions if p not in admin_permissions]
        if missing_permissions:
            self.log_test("Admin Role Assignment Permissions", False, 
                f"Admin role missing permissions: {missing_permissions}")
            return False
        
        return True

    def test_security_validation(self):
        """Test security validation scenarios"""
        # Test password reset requires minimum 6 characters (already tested in test_admin_password_reset)
        
        # Test invalid permission assignments are rejected (already tested in test_admin_permission_management)
        
        # Test proper authorization checks on all admin endpoints
        admin_endpoints = [
            ("GET", "permissions/available"),
            ("GET", "users"),
            ("POST", "users/reset-password", {"user_id": "test", "new_password": "password123"}),
            ("DELETE", "users/test-user-id"),
            ("PUT", "users/test-user-id/permissions", {"user_id": "test", "permissions": ["view_dashboard"]})
        ]
        
        success_count = 0
        total_endpoints = len(admin_endpoints)
        
        for method, endpoint, *data in admin_endpoints:
            request_data = data[0] if data else None
            
            # Test regular user gets 403 for admin endpoints
            result = self.run_api_test(
                f"Security Validation - {method} {endpoint} (Regular User Should Fail)",
                method,
                endpoint,
                403,
                data=request_data,
                token=self.user_token
            )
            
            if result is not None:  # 403 was returned as expected
                success_count += 1
        
        # Test edge cases with empty permission lists
        empty_permissions_data = {
            "user_id": self.regular_user_data['id'],
            "permissions": []
        }
        
        empty_result = self.run_api_test(
            "Security Validation - Empty Permissions Assignment",
            "PUT",
            f"users/{self.regular_user_data['id']}/permissions",
            200,
            data=empty_permissions_data,
            token=self.admin_token
        )
        
        if empty_result:
            success_count += 1
            total_endpoints += 1
        
        return success_count == total_endpoints

    def run_all_tests(self):
        """Run all permission system tests"""
        print("🔐 Starting Permission-Based Access Control System Testing...")
        print("=" * 80)
        
        # Setup test users
        if not self.setup_test_users():
            print("❌ Failed to setup test users. Aborting tests.")
            return False
        
        print(f"✅ Test users created successfully")
        print(f"   Admin: {self.admin_user_data['email']}")
        print(f"   Regular User: {self.regular_user_data['email']}")
        print()
        
        # Run all test categories
        test_categories = [
            ("Permission System Testing", [
                self.test_get_available_permissions,
                self.test_get_user_permissions
            ]),
            ("Admin User Management Testing", [
                self.test_admin_password_reset,
                self.test_admin_user_deletion,
                self.test_admin_permission_management
            ]),
            ("Permission-Based Access Control Testing", [
                self.test_permission_based_access_control
            ]),
            ("User Creation and Default Permissions", [
                self.test_user_creation_default_permissions
            ]),
            ("Security Validation", [
                self.test_security_validation
            ])
        ]
        
        all_passed = True
        
        for category_name, tests in test_categories:
            print(f"📋 {category_name}")
            print("-" * 60)
            
            category_passed = 0
            category_total = len(tests)
            
            for test_func in tests:
                try:
                    if test_func():
                        category_passed += 1
                    else:
                        all_passed = False
                except Exception as e:
                    self.log_test(f"{test_func.__name__}", False, f"Exception: {str(e)}")
                    all_passed = False
            
            print(f"   Category Results: {category_passed}/{category_total} tests passed")
            print()
        
        # Print final summary
        print("=" * 80)
        print("🏁 PERMISSION SYSTEM TESTING SUMMARY")
        print("=" * 80)
        print(f"Total Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run)*100:.1f}%")
        
        if all_passed:
            print("🎉 ALL PERMISSION SYSTEM TESTS PASSED!")
        else:
            print("⚠️  Some tests failed. Check details above.")
        
        return all_passed

if __name__ == "__main__":
    tester = PermissionSystemTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)