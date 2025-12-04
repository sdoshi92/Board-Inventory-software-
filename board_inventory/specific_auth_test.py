#!/usr/bin/env python3
"""
Specific Authentication Test for provided credentials
Tests the authentication system with the specific credentials mentioned in the review request.
"""

import requests
import json
from datetime import datetime

def test_specific_credentials():
    """Test authentication with the specific credentials provided in the review request"""
    base_url = "http://localhost:8001"
    api_url = f"{base_url}/api"
    
    print("🔐 Testing Specific Authentication Credentials")
    print("=" * 50)
    
    # Test credentials from review request
    test_email = "testlogin@example.com"
    test_password = "password123"
    
    # Test 1: Login with provided credentials
    print("\n=== Testing Login with Provided Credentials ===")
    login_data = {
        "email": test_email,
        "password": test_password
    }
    
    try:
        response = requests.post(f"{api_url}/auth/login", json=login_data, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            if 'access_token' in response_data and 'user' in response_data:
                token = response_data['access_token']
                user = response_data['user']
                print("✅ Login successful!")
                print(f"   Token: {token[:30]}...")
                print(f"   User Email: {user.get('email')}")
                print(f"   User Role: {user.get('role')}")
                print(f"   User Name: {user.get('first_name')} {user.get('last_name')}")
                
                # Test 2: Use token to access protected endpoint
                print("\n=== Testing Token with Protected Endpoint ===")
                headers = {'Authorization': f'Bearer {token}'}
                me_response = requests.get(f"{api_url}/auth/me", headers=headers, timeout=10)
                
                print(f"Status Code: {me_response.status_code}")
                if me_response.status_code == 200:
                    me_data = me_response.json()
                    print("✅ Token validation successful!")
                    print(f"   Verified User: {me_data.get('email')}")
                    print(f"   User ID: {me_data.get('id')}")
                    print(f"   Active: {me_data.get('is_active')}")
                else:
                    print("❌ Token validation failed!")
                    print(f"   Error: {me_response.text}")
                
                # Test 3: Try to access categories (might be permission restricted)
                print("\n=== Testing Access to Categories Endpoint ===")
                cat_response = requests.get(f"{api_url}/categories", headers=headers, timeout=10)
                print(f"Status Code: {cat_response.status_code}")
                
                if cat_response.status_code == 200:
                    categories = cat_response.json()
                    print(f"✅ Categories access successful! Found {len(categories)} categories")
                elif cat_response.status_code == 403:
                    print("⚠️  Categories access forbidden (permission issue, but token is valid)")
                else:
                    print("❌ Categories access failed!")
                    print(f"   Error: {cat_response.text}")
                
                return True
            else:
                print("❌ Login response missing required fields")
                print(f"   Response: {response_data}")
                return False
        else:
            print("❌ Login failed!")
            try:
                error_data = response.json()
                print(f"   Error: {error_data.get('detail', 'Unknown error')}")
            except:
                print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def test_create_test_user():
    """Create the test user if it doesn't exist"""
    base_url = "http://localhost:8001"
    api_url = f"{base_url}/api"
    
    print("\n=== Creating Test User (if needed) ===")
    
    # Try to create the test user
    registration_data = {
        "email": "testlogin@example.com",
        "first_name": "Test",
        "last_name": "User",
        "designation": "Test Engineer",
        "password": "password123"
    }
    
    try:
        response = requests.post(f"{api_url}/auth/register", json=registration_data, timeout=10)
        print(f"Registration Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Test user created successfully!")
            return True
        elif response.status_code == 400:
            error_data = response.json()
            if "Email already registered" in error_data.get('detail', ''):
                print("ℹ️  Test user already exists")
                return True
            else:
                print(f"❌ Registration failed: {error_data.get('detail')}")
                return False
        else:
            print(f"❌ Registration failed with status {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Registration request failed: {e}")
        return False

if __name__ == "__main__":
    print("🔐 Specific Authentication Testing")
    print("Testing with credentials: testlogin@example.com / password123")
    print("=" * 60)
    
    # First try to create the test user
    user_created = test_create_test_user()
    
    if user_created:
        # Then test authentication
        auth_success = test_specific_credentials()
        
        print("\n" + "=" * 60)
        if auth_success:
            print("✅ All specific authentication tests passed!")
        else:
            print("❌ Some authentication tests failed!")
    else:
        print("❌ Could not create/verify test user!")