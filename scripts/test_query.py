import requests
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_URL = "http://127.0.0.1:8000"
USER_EMAIL = "test@example.com"
USER_PASSWORD = "securepassword"

def test_query():
    # 1. Login
    print("Logging in...")
    response = requests.post(f"{BASE_URL}/token", json={"email": USER_EMAIL, "password": USER_PASSWORD})
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    token = response.json()["access_token"]
    
    # 2. Ask Question
    question = "What is this document about?"
    print(f"Asking: '{question}'")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/chat", 
        json={"question": question}, 
        headers=headers
    )
    
    if response.status_code == 200:
        print("\n--- Response ---")
        print(response.json()["answer"])
        print("----------------")
    else:
        print(f"Query failed: {response.text}")

if __name__ == "__main__":
    test_query()
