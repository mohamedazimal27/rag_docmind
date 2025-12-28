import os
import chromadb
from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# Create single embedding function instance to save resources? 
# Or create per request. OpenAIEmbeddings is lightweight client.
embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")

def get_vectorstore_path(user_id: int) -> str:
    return str(DATA_DIR / str(user_id) / "chroma_db")

def add_documents_to_chroma(user_id: int, chunks: list):
    """
    Adds documents to the user's dedicated ChromaDB collection.
    """
    persist_directory = get_vectorstore_path(user_id)
    
    # Initialize Chroma vector store with persistence
    # We use LangChain's Chroma wrapper for easy integration
    vectorstore = Chroma(
        collection_name=f"user_{user_id}_docs",
        embedding_function=embedding_function,
        persist_directory=persist_directory
    )
    
    vectorstore.add_documents(chunks)
    vectorstore.persist()
    # print(f"Added {len(chunks)} chunks to ChromaDB for user {user_id} at {persist_directory}")

def get_vectorstore(user_id: int):
    """
    Returns the ready-to-use vectorstore for retrieval.
    """
    persist_directory = get_vectorstore_path(user_id)
    return Chroma(
        collection_name=f"user_{user_id}_docs",
        embedding_function=embedding_function,
        persist_directory=persist_directory
    )
