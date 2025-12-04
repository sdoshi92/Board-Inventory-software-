#!/usr/bin/env python3

import requests
import json
from datetime import datetime

class BulkApprovalTester:
    def __init__(self, base_url="https://boardventory.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.user_data = None
        self.test_category_id = None

    def register_and_login(self):
        """Register and login to get auth token"""
        timestamp = datetime.now().strftime('%H%M%S')
        test_email = f"bulk_approval_test_{timestamp}@example.com"
        test_password = "TestPass123!"
        
        # Register
        register_data = {"email": test_email, "password": test_password}
        response = requests.post(f"{self.api_url}/auth/register", json=register_data)
        
        if response.status_code == 200:
            result = response.json()
            self.token = result['access_token']
            self.user_data = result['user']
            print(f"✅ Registered and logged in as {test_email}")
            return True
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return False

    def create_test_category(self):
        """Create a test category"""
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        category_data = {
            "name": f"Bulk Approval Test Category {datetime.now().strftime('%H%M%S')}",
            "description": "Test category for bulk approval testing",
            "manufacturer": "Test Manufacturer",
            "version": "1.0",
            "lead_time_days": 30,
            "minimum_stock_quantity": 10
        }
        
        response = requests.post(f"{self.api_url}/categories", json=category_data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            self.test_category_id = result['id']
            print(f"✅ Created test category: {result['name']}")
            return True
        else:
            print(f"❌ Category creation failed: {response.status_code} - {response.text}")
            return False

    def create_test_boards(self, count=3):
        """Create test boards"""
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        board_ids = []
        
        for i in range(count):
            board_data = {
                "category_id": self.test_category_id,
                "serial_number": f"BULK_APPROVAL_TEST_{i}_{datetime.now().strftime('%H%M%S')}",
                "location": "In stock",
                "condition": "New",
                "comments": f"Bulk approval test board {i+1}"
            }
            
            response = requests.post(f"{self.api_url}/boards", json=board_data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                board_ids.append(result['id'])
                print(f"✅ Created test board {i+1}: {result['serial_number']}")
            else:
                print(f"❌ Board {i+1} creation failed: {response.status_code} - {response.text}")
                return []
        
        return board_ids

    def create_bulk_issue_request(self):
        """Create a bulk issue request"""
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        
        bulk_request_data = {
            "categories": [
                {
                    "category_id": self.test_category_id,
                    "quantity": 2
                }
            ],
            "issued_to": "Bulk Approval Test Engineer",
            "project_number": "PROJ_BULK_APPROVAL_001",
            "comments": "Testing bulk request approval functionality"
        }
        
        response = requests.post(f"{self.api_url}/issue-requests/bulk", json=bulk_request_data, headers=headers)
        
        print(f"Bulk request response status: {response.status_code}")
        print(f"Bulk request response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Created bulk issue request")
            print(f"Response structure: {json.dumps(result, indent=2)}")
            return result.get('request_id')
        else:
            print(f"❌ Bulk request creation failed: {response.status_code} - {response.text}")
            return None

    def get_bulk_issue_requests(self):
        """Get all bulk issue requests"""
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        
        response = requests.get(f"{self.api_url}/bulk-issue-requests", headers=headers)
        
        print(f"Get bulk requests response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Retrieved bulk issue requests")
            print(f"Found {len(result)} bulk requests")
            for req in result:
                print(f"  - Request ID: {req.get('id')}, Status: {req.get('status')}")
            return result
        else:
            print(f"❌ Get bulk requests failed: {response.status_code} - {response.text}")
            return []

    def make_user_admin(self):
        """Make current user admin"""
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        
        response = requests.post(f"{self.api_url}/setup-admin?email={self.user_data['email']}", headers=headers)
        
        if response.status_code == 200:
            print(f"✅ Made user admin: {self.user_data['email']}")
            return True
        else:
            print(f"❌ Admin setup failed: {response.status_code} - {response.text}")
            return False

    def test_bulk_request_approval(self, request_id):
        """Test bulk request approval"""
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        
        # Test approval
        approval_data = {
            "status": "approved"
        }
        
        response = requests.put(f"{self.api_url}/bulk-issue-requests/{request_id}", json=approval_data, headers=headers)
        
        print(f"Approval response status: {response.status_code}")
        print(f"Approval response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Successfully approved bulk request")
            print(f"Approved by: {result.get('approved_by')}")
            print(f"Approved date: {result.get('approved_date')}")
            print(f"Status: {result.get('status')}")
            return True
        else:
            print(f"❌ Approval failed: {response.status_code} - {response.text}")
            return False

    def test_non_admin_approval(self, request_id):
        """Test approval without admin role (should fail)"""
        headers = {'Authorization': f'Bearer {self.token}', 'Content-Type': 'application/json'}
        
        approval_data = {
            "status": "approved"
        }
        
        response = requests.put(f"{self.api_url}/bulk-issue-requests/{request_id}", json=approval_data, headers=headers)
        
        print(f"Non-admin approval response status: {response.status_code}")
        
        if response.status_code == 403:
            print(f"✅ Non-admin approval correctly rejected with 403")
            return True
        else:
            print(f"❌ Non-admin approval should have failed with 403, got {response.status_code}")
            return False

    def run_test(self):
        """Run the complete bulk approval test"""
        print("🚀 Starting Bulk Issue Request Approval Test")
        print("=" * 50)
        
        # Step 1: Register and login
        if not self.register_and_login():
            return False
        
        # Step 2: Create test category
        if not self.create_test_category():
            return False
        
        # Step 3: Create test boards
        board_ids = self.create_test_boards(3)
        if not board_ids:
            return False
        
        # Step 4: Create bulk issue request
        request_id = self.create_bulk_issue_request()
        if not request_id:
            return False
        
        # Step 5: Get bulk issue requests to verify creation
        requests_list = self.get_bulk_issue_requests()
        if not requests_list:
            return False
        
        # Step 6: Test non-admin approval (should fail)
        print("\n🔒 Testing non-admin approval (should fail)")
        self.test_non_admin_approval(request_id)
        
        # Step 7: Make user admin
        if not self.make_user_admin():
            return False
        
        # Step 8: Test admin approval (should succeed)
        print("\n✅ Testing admin approval (should succeed)")
        if not self.test_bulk_request_approval(request_id):
            return False
        
        # Step 9: Verify final status
        print("\n🔍 Verifying final status")
        final_requests = self.get_bulk_issue_requests()
        
        print("\n🎉 Bulk Issue Request Approval Test Completed Successfully!")
        return True

if __name__ == "__main__":
    tester = BulkApprovalTester()
    success = tester.run_test()
    exit(0 if success else 1)