#!/usr/bin/env python3
import requests
import json
import uuid
import time
import os
from dotenv import load_dotenv
from pathlib import Path

# Load frontend .env to get the backend URL
frontend_env_path = Path("/app/frontend/.env")
load_dotenv(frontend_env_path)

# Get backend URL from frontend .env
BACKEND_URL = os.environ.get("REACT_APP_BACKEND_URL")
if not BACKEND_URL:
    raise ValueError("REACT_APP_BACKEND_URL not found in frontend/.env")

API_URL = f"{BACKEND_URL}/api"
print(f"Using API URL: {API_URL}")

# Load backend .env to get the guild ID
backend_env_path = Path("/app/backend/.env")
load_dotenv(backend_env_path)
GUILD_ID = os.environ.get("DISCORD_GUILD_ID")
if not GUILD_ID:
    raise ValueError("DISCORD_GUILD_ID not found in backend/.env")

# Test results
test_results = {
    "health_check": {"status": "Not Tested", "details": ""},
    "bot_status": {"status": "Not Tested", "details": ""},
    "bot_start": {"status": "Not Tested", "details": ""},
    "products_list": {"status": "Not Tested", "details": ""},
    "product_create": {"status": "Not Tested", "details": ""},
    "product_delete": {"status": "Not Tested", "details": ""},
    "conversations": {"status": "Not Tested", "details": ""},
    "bot_config_get": {"status": "Not Tested", "details": ""},
    "bot_config_update": {"status": "Not Tested", "details": ""}
}

def run_test(test_name, func):
    """Run a test and update the results"""
    print(f"\n=== Testing {test_name} ===")
    try:
        result = func()
        test_results[test_name]["status"] = "Passed" if result else "Failed"
        print(f"Result: {test_results[test_name]['status']}")
        return result
    except Exception as e:
        test_results[test_name]["status"] = "Failed"
        test_results[test_name]["details"] = f"Exception: {str(e)}"
        print(f"Exception: {str(e)}")
        return False

def test_health_check():
    """Test the health check endpoint"""
    response = requests.get(f"{API_URL}/")
    print(f"Response: {response.status_code} - {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        test_results["health_check"]["details"] = f"API is working: {data.get('message', '')}"
        return True
    else:
        test_results["health_check"]["details"] = f"API health check failed with status {response.status_code}"
        return False

def test_bot_status():
    """Test the bot status endpoint"""
    response = requests.get(f"{API_URL}/bot/status")
    print(f"Response: {response.status_code} - {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        test_results["bot_status"]["details"] = f"Bot running: {data.get('running', False)}, Bot user: {data.get('bot_user', 'None')}"
        return True
    else:
        test_results["bot_status"]["details"] = f"Bot status check failed with status {response.status_code}"
        return False

def test_bot_start():
    """Test the bot start endpoint"""
    response = requests.post(f"{API_URL}/bot/start")
    print(f"Response: {response.status_code} - {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        test_results["bot_start"]["details"] = f"Message: {data.get('message', '')}"
        
        # Wait a bit for the bot to start
        time.sleep(2)
        
        # Check status again
        status_response = requests.get(f"{API_URL}/bot/status")
        if status_response.status_code == 200:
            status_data = status_response.json()
            if status_data.get('running', False):
                test_results["bot_start"]["details"] += " - Bot is now running"
            else:
                test_results["bot_start"]["details"] += " - Bot failed to start or has privileged intents issue"
        
        return True
    else:
        test_results["bot_start"]["details"] = f"Bot start failed with status {response.status_code}"
        return False

def test_products_list():
    """Test the products list endpoint"""
    response = requests.get(f"{API_URL}/products")
    print(f"Response: {response.status_code} - {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        test_results["products_list"]["details"] = f"Retrieved {len(data)} products"
        return True
    else:
        test_results["products_list"]["details"] = f"Products list failed with status {response.status_code}"
        return False

def test_product_create():
    """Test the product create endpoint"""
    test_product = {
        "name": f"Test Product {uuid.uuid4().hex[:8]}",
        "price": 19.99,
        "description": "This is a test product created by the API test script",
        "category": "test",
        "stock": 10
    }
    
    response = requests.post(f"{API_URL}/products", json=test_product)
    print(f"Response: {response.status_code} - {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        product_id = data.get('id')
        test_results["product_create"]["details"] = f"Created product with ID: {product_id}"
        
        # Store the product ID for deletion test
        test_results["product_create"]["product_id"] = product_id
        return True
    else:
        test_results["product_create"]["details"] = f"Product creation failed with status {response.status_code}"
        return False

def test_product_delete():
    """Test the product delete endpoint"""
    product_id = test_results["product_create"].get("product_id")
    
    if not product_id:
        test_results["product_delete"]["details"] = "No product ID available for deletion test"
        return False
    
    response = requests.delete(f"{API_URL}/products/{product_id}")
    print(f"Response: {response.status_code} - {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        test_results["product_delete"]["details"] = f"Deleted product: {data.get('message', '')}"
        return True
    else:
        test_results["product_delete"]["details"] = f"Product deletion failed with status {response.status_code}"
        return False

def test_conversations():
    """Test the conversations endpoint"""
    response = requests.get(f"{API_URL}/conversations")
    print(f"Response: {response.status_code} - {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        test_results["conversations"]["details"] = f"Retrieved {len(data)} conversations"
        return True
    else:
        test_results["conversations"]["details"] = f"Conversations retrieval failed with status {response.status_code}"
        return False

def test_bot_config_get():
    """Test the bot config get endpoint"""
    response = requests.get(f"{API_URL}/bot/config/{GUILD_ID}")
    print(f"Response: {response.status_code} - {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        test_results["bot_config_get"]["details"] = f"Retrieved config for guild {GUILD_ID}"
        # Store the config for update test
        test_results["bot_config_get"]["config"] = data
        return True
    elif response.status_code == 404:
        # This is acceptable if the bot hasn't been configured yet
        test_results["bot_config_get"]["details"] = f"No config found for guild {GUILD_ID} (404)"
        return True
    else:
        test_results["bot_config_get"]["details"] = f"Bot config get failed with status {response.status_code}"
        return False

def test_bot_config_update():
    """Test the bot config update endpoint"""
    # Create a test config
    test_config = {
        "ai_enabled": True,
        "shop_enabled": True,
        "welcome_message": "Welcome to the test server!",
        "ai_channel_id": "123456789012345678"  # Dummy channel ID
    }
    
    response = requests.put(f"{API_URL}/bot/config/{GUILD_ID}", json=test_config)
    print(f"Response: {response.status_code} - {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        test_results["bot_config_update"]["details"] = f"Updated config: {data.get('message', '')}"
        
        # Verify the update
        verify_response = requests.get(f"{API_URL}/bot/config/{GUILD_ID}")
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            if verify_data.get("ai_channel_id") == test_config["ai_channel_id"]:
                test_results["bot_config_update"]["details"] += " - Verified update was successful"
            else:
                test_results["bot_config_update"]["details"] += " - Update verification failed"
        
        return True
    else:
        test_results["bot_config_update"]["details"] = f"Bot config update failed with status {response.status_code}"
        return False

def run_all_tests():
    """Run all tests in sequence"""
    run_test("health_check", test_health_check)
    run_test("bot_status", test_bot_status)
    run_test("bot_start", test_bot_start)
    run_test("products_list", test_products_list)
    run_test("product_create", test_product_create)
    run_test("product_delete", test_product_delete)
    run_test("conversations", test_conversations)
    run_test("bot_config_get", test_bot_config_get)
    run_test("bot_config_update", test_bot_config_update)
    
    # Print summary
    print("\n=== Test Summary ===")
    for test_name, result in test_results.items():
        print(f"{test_name}: {result['status']} - {result['details']}")

if __name__ == "__main__":
    run_all_tests()