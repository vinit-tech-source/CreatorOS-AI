import requests
import json
import traceback

data = {
    "username": "testuser_abc",
    "full_name": "Test User ABC",
    "email": "test_abc@example.com",
    "password": "Password123!"
}

try:
    # Explicitly use 127.0.0.1 instead of localhost
    response = requests.post("http://127.0.0.1:8000/api/v1/auth/register", json=data)
    print("STATUS:", response.status_code)
    print("RESPONSE:", response.text)
except Exception as e:
    print("Error:")
    traceback.print_exc()
