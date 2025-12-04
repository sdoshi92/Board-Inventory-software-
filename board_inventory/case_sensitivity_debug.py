import requests
from datetime import datetime

def debug_case_sensitivity():
    """Debug case sensitivity issue"""
    base_url = "https://boardventory.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    timestamp = datetime.now().strftime('%H%M%S')
    
    # Register user with mixed case email
    registration_data = {
        "email": f"CaseTest_{timestamp}@Example.COM",
        "first_name": "Case",
        "last_name": "Test",
        "designation": "Test Engineer",
        "password": "CaseTest123!"
    }
    
    print("Registering user with mixed case email...")
    reg_response = requests.post(f"{api_url}/auth/register", json=registration_data, timeout=10)
    print(f"Registration status: {reg_response.status_code}")
    
    if reg_response.status_code == 200:
        result = reg_response.json()
        registered_email = result['user']['email']
        print(f"Registered email: {registered_email}")
        
        # Try login with exact same case
        print("\nTrying login with exact same case...")
        login_data1 = {
            "email": registered_email,
            "password": "CaseTest123!"
        }
        
        login_response1 = requests.post(f"{api_url}/auth/login", json=login_data1, timeout=10)
        print(f"Same case login status: {login_response1.status_code}")
        if login_response1.status_code != 200:
            print(f"Error: {login_response1.text}")
        
        # Try login with lowercase
        print("\nTrying login with lowercase...")
        login_data2 = {
            "email": registered_email.lower(),
            "password": "CaseTest123!"
        }
        
        login_response2 = requests.post(f"{api_url}/auth/login", json=login_data2, timeout=10)
        print(f"Lowercase login status: {login_response2.status_code}")
        if login_response2.status_code != 200:
            print(f"Error: {login_response2.text}")
        
        # Try login with uppercase
        print("\nTrying login with uppercase...")
        login_data3 = {
            "email": registered_email.upper(),
            "password": "CaseTest123!"
        }
        
        login_response3 = requests.post(f"{api_url}/auth/login", json=login_data3, timeout=10)
        print(f"Uppercase login status: {login_response3.status_code}")
        if login_response3.status_code != 200:
            print(f"Error: {login_response3.text}")

if __name__ == "__main__":
    debug_case_sensitivity()