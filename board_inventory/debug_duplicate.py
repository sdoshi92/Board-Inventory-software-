import requests
import json
from datetime import datetime

def test_duplicate_validation():
    """Simple test to debug duplicate validation"""
    base_url = "https://boardventory.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    # Register user
    timestamp = datetime.now().strftime('%H%M%S')
    test_email = f"debug_user_{timestamp}@example.com"
    test_password = "DebugTest123!"
    
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
    
    # Create category
    category_response = requests.post(f"{api_url}/categories", json={
        "name": f"Debug Category {timestamp}",
        "description": "Debug category",
        "manufacturer": "Debug Manufacturer",
        "version": "1.0",
        "lead_time_days": 30,
        "minimum_stock_quantity": 10
    }, headers=headers)
    
    if category_response.status_code != 200:
        print(f"Category creation failed: {category_response.status_code} - {category_response.text}")
        return
    
    category_id = category_response.json()['id']
    duplicate_serial = f"DEBUG_DUPLICATE_{timestamp}"
    
    # Create first board
    board1_response = requests.post(f"{api_url}/boards", json={
        "category_id": category_id,
        "serial_number": duplicate_serial,
        "location": "In stock",
        "condition": "New"
    }, headers=headers)
    
    print(f"First board creation: {board1_response.status_code}")
    if board1_response.status_code == 200:
        print(f"First board created successfully: {board1_response.json()['id']}")
    else:
        print(f"First board creation failed: {board1_response.text}")
        return
    
    # Try to create duplicate board
    board2_response = requests.post(f"{api_url}/boards", json={
        "category_id": category_id,
        "serial_number": duplicate_serial,  # Same serial number
        "location": "In stock", 
        "condition": "New"
    }, headers=headers)
    
    print(f"Duplicate board creation: {board2_response.status_code}")
    if board2_response.status_code == 400:
        print(f"✅ Duplicate properly rejected: {board2_response.json()}")
    else:
        print(f"❌ Duplicate was NOT rejected: {board2_response.text}")
        if board2_response.status_code == 200:
            print(f"Duplicate board was created: {board2_response.json()['id']}")
    
    # Cleanup
    if board1_response.status_code == 200:
        board1_id = board1_response.json()['id']
        requests.delete(f"{api_url}/boards/{board1_id}", headers=headers)
    
    if board2_response.status_code == 200:
        board2_id = board2_response.json()['id']
        requests.delete(f"{api_url}/boards/{board2_id}", headers=headers)
    
    requests.delete(f"{api_url}/categories/{category_id}", headers=headers)

if __name__ == "__main__":
    test_duplicate_validation()