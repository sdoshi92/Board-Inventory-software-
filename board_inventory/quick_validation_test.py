import requests
from datetime import datetime

def test_empty_string_validation():
    """Test that empty strings are now properly rejected"""
    base_url = "https://boardventory.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    timestamp = datetime.now().strftime('%H%M%S')
    
    # Test empty first name
    registration_data = {
        "email": f"empty_test_{timestamp}@example.com",
        "first_name": "",  # Empty string
        "last_name": "Doe",
        "designation": "Engineer",
        "password": "SecurePass123!"
    }
    
    response = requests.post(f"{api_url}/auth/register", json=registration_data, timeout=10)
    print(f"Empty first name test: Status {response.status_code}")
    if response.status_code == 422:
        print("✅ Empty string validation working!")
        return True
    else:
        print("❌ Empty string validation not working")
        return False

def test_backward_compatibility():
    """Test that existing users can still login"""
    base_url = "https://boardventory.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    # First register a new user with all fields
    timestamp = datetime.now().strftime('%H%M%S')
    registration_data = {
        "email": f"compat_test_{timestamp}@example.com",
        "first_name": "Compat",
        "last_name": "Test",
        "designation": "Test Engineer",
        "password": "CompatTest123!"
    }
    
    reg_response = requests.post(f"{api_url}/auth/register", json=registration_data, timeout=10)
    print(f"Registration test: Status {reg_response.status_code}")
    
    if reg_response.status_code == 200:
        # Try to login
        login_data = {
            "email": registration_data["email"],
            "password": registration_data["password"]
        }
        
        login_response = requests.post(f"{api_url}/auth/login", json=login_data, timeout=10)
        print(f"Login test: Status {login_response.status_code}")
        
        if login_response.status_code == 200:
            print("✅ Backward compatibility working!")
            return True
        else:
            print("❌ Login failed")
            return False
    else:
        print("❌ Registration failed")
        return False

if __name__ == "__main__":
    print("🔧 Testing fixes...")
    
    test1 = test_empty_string_validation()
    test2 = test_backward_compatibility()
    
    if test1 and test2:
        print("\n🎉 All fixes working correctly!")
    else:
        print("\n⚠️ Some issues remain")