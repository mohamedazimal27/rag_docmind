import requests
import os
import chromadb
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv

load_dotenv()

# Configuration
BASE_URL = "http://127.0.0.1:8000"
USER_EMAIL = "test@example.com"
USER_PASSWORD = "securepassword"
TEST_FILE_PATH = "sample.pdf"

# Create a dummy PDF for testing
from fpdf import FPDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="This is a test document for DocuMind Pro.", ln=1, align="C")
pdf.cell(200, 10, txt="It contains information about RAG systems.", ln=2, align="C")
pdf.output(TEST_FILE_PATH)

def test_upload_and_verify():
    # 1. Login
    print("Logging in...")
    response = requests.post(f"{BASE_URL}/token", json={"email": USER_EMAIL, "password": USER_PASSWORD})
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        return
    token = response.json()["access_token"]
    print(f"Got token: {token[:10]}...")

    # 2. Upload
    print(f"Uploading {TEST_FILE_PATH}...")
    with open(TEST_FILE_PATH, "rb") as f:
        files = {"file": f}
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/upload", files=files, headers=headers)
    
    if response.status_code == 200:
        print("Upload success!", response.json())
        result = response.json()
        if result["chunks_processed"] > 0:
            print("Verified: Backend reports chunks processed.")
        else:
            print("Warning: 0 chunks processed.")
    else:
        print(f"Upload failed: {response.text}")
        return

    # 3. Verify ChromaDB
    # Assuming user_id=1 for test@example.com
    user_id = 1
    persist_directory = f"data/{user_id}/chroma_db"
    
    print(f"Checking ChromaDB at {persist_directory}...")
    
    try:
        embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")
        vectorstore = Chroma(
            collection_name=f"user_{user_id}_docs",
            embedding_function=embedding_function,
            persist_directory=persist_directory
        )
        # We need to force reload or check count differently if it's persistent?
        # Creating a new client usually reads from disk.
        
        # NOTE: Chroma persistent client requires the db to be flushed. 
        # The backend triggers persist().
        
        count = len(vectorstore.get()['ids'])
        print(f"ChromaDB Collection Count: {count}")
        
        if count > 0:
            print("SUCCESS: Vectors found in ChromaDB.")
        else:
            print("FAILURE: No vectors found in ChromaDB.")
            
    except Exception as e:
        print(f"Error checking Chroma: {e}")

if __name__ == "__main__":
    test_upload_and_verify()
