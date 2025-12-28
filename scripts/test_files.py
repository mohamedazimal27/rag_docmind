import requests
from dotenv import load_dotenv
import os

load_dotenv()

BASE_URL = "http://127.0.0.1:8000"
USER_EMAIL = "test@example.com"
USER_PASSWORD = "securepassword"

def test_files():
    # Login
    print("Logging in...")
    response = requests.post(f"{BASE_URL}/token", json={"email": USER_EMAIL, "password": USER_PASSWORD})
    if response.status_code != 200:
        print("Login failed")
        return
    token = response.json()["access_token"]
    
    # Get Files
    print("Fetching files...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/files", headers=headers)
    
    if response.status_code == 200:
        print("Files:", response.json())
        if "sample.pdf" in response.json()["files"]:
            print("SUCCESS: sample.pdf found in file list.")
        else:
            print("WARNING: sample.pdf not found (did you upload it?).")
    else:
        print(f"Failed to get files: {response.text}")

if __name__ == "__main__":
    test_files()
