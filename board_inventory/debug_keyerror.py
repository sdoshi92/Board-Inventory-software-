import requests
import json
from datetime import datetime

def test_keyerror_debug():
    base_url = "https://boardventory.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    # Register user
    timestamp = datetime.now().strftime('%H%M%S')
    test_email = f"debug_test_{timestamp}@example.com"
    test_password = "TestPass123!"
    
    # Register
    response = requests.post(f"{api_url}/auth/register", json={
        "email": test_email, 
        "password": test_password
    })
    
    if response.status_code != 200:
        print(f"Registration failed: {response.status_code} - {response.text}")
        return
    
    token = response.json()['access_token']
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    
    print("🔍 Testing specific KeyError scenario...")
    
    # Test 1: Completely nonexistent category
    print("\n1. Testing completely nonexistent category:")
    bulk_request_data = {
        "categories": [
            {
                "category_id": "completely-fake-id-12345",
                "quantity": 1
            }
        ],
        "issued_to": "Debug Test Engineer",
        "project_number": "DEBUG_001",
        "comments": "Debug test"
    }
    
    response = requests.post(f"{api_url}/issue-requests/bulk", json=bulk_request_data, headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # Test 2: Create a category, then test with insufficient stock
    print("\n2. Creating category for insufficient stock test:")
    category_data = {
        "name": f"Debug Category {timestamp}",
        "description": "Debug test category",
        "manufacturer": "Debug Manufacturer",
        "version": "1.0",
        "lead_time_days": 30,
        "minimum_stock_quantity": 10
    }
    
    response = requests.post(f"{api_url}/categories", json=category_data, headers=headers)
    if response.status_code == 200:
        category_id = response.json()['id']
        print(f"Created category: {category_id}")
        
        # Test insufficient stock (no boards created)
        print("\n3. Testing insufficient stock scenario:")
        bulk_request_data = {
            "categories": [
                {
                    "category_id": category_id,
                    "quantity": 1
                }
            ],
            "issued_to": "Debug Test Engineer",
            "project_number": "DEBUG_002",
            "comments": "Debug insufficient stock test"
        }
        
        response = requests.post(f"{api_url}/issue-requests/bulk", json=bulk_request_data, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        # Cleanup
        requests.delete(f"{api_url}/categories/{category_id}", headers=headers)
    else:
        print(f"Failed to create category: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_keyerror_debug()