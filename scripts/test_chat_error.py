import requests
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = "http://127.0.0.1:8000"
USER_EMAIL = "test@example.com"
USER_PASSWORD = "securepassword"

def test_chat():
    print("1. Logging in...")
    try:
        response = requests.post(f"{BASE_URL}/token", json={"email": USER_EMAIL, "password": USER_PASSWORD})
        if response.status_code != 200:
            print(f"Login failed: {response.text}")
            return
        token = response.json()["access_token"]
        print("Login success.")
    except Exception as e:
        print(f"Login Connection Refused/Error: {e}")
        return

    print("2. Sending Query...")
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.post(
            f"{BASE_URL}/chat", 
            json={"question": "What is this document about?"},
            headers=headers
        )
        
        if response.status_code == 200:
            print("Chat Response:", response.json())
        else:
            print(f"Chat Failed [Status {response.status_code}]:")
            print(response.text) # This will show the stack trace if it's a 500
    except Exception as e:
        print(f"Chat Connection Error: {e}")

if __name__ == "__main__":
    test_chat()
