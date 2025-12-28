import chromadb
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
import os
import sys

# Add backend to path to import modules if needed, though we rely on standard libs here
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

load_dotenv()

def debug_rag(user_id=1, query="What is the energy document about?"):
    print(f"--- Debugging RAG for User {user_id} ---")
    
    # 1. Initialize Vector Store
    persist_directory = f"data/{user_id}/chroma_db"
    if not os.path.exists(persist_directory):
        print(f"ERROR: Persist directory {persist_directory} does not exist.")
        return

    print(f"Loading ChromaDB from {persist_directory}...")
    embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")
    
    vectorstore = Chroma(
        collection_name=f"user_{user_id}_docs",
        embedding_function=embedding_function,
        persist_directory=persist_directory
    )
    
    # 2. Check Collection Stats
    # LangChain's Chroma wrapper doesn't expose 'get' easily for all docs without query
    # But we can assume some basic stats or use the client directly if needed.
    # Let's try to get all IDs.
    try:
        collection_data = vectorstore.get()
        ids = collection_data['ids']
        metadatas = collection_data['metadatas']
        print(f"Total Chunks in DB: {len(ids)}")
        
        # Analyze Sources
        sources = set()
        for m in metadatas:
            if m and "document_name" in m:
                sources.add(m["document_name"])
        print(f"Unique Sources Found: {sources}")
        
    except Exception as e:
        print(f"Error inspecting collection stats: {e}")

    # 3. Simulate Retrieval
    print(f"\n--- Simulating Retrieval for query: '{query}' ---")
    try:
        # Applying the same filter as rag.py
        results = vectorstore.similarity_search(
            query, 
            k=4,
            filter={"user_id": user_id} 
        )
        
        if not results:
            print("No documents retrieved.")
        else:
            print(f"Retrieved {len(results)} chunks:")
            for i, doc in enumerate(results):
                print(f"\n[Chunk {i+1}]")
                print(f"Source: {doc.metadata.get('document_name', 'Unknown')}")
                print(f"Page/Row: {doc.metadata.get('page_number') or doc.metadata.get('row_range', 'Unknown')}")
                print(f"Score: (Not available in standard similarity_search)") 
                print(f"Content Preview: {doc.page_content[:200]}...") # Show first 200 chars
                
    except Exception as e:
        print(f"Error during retrieval: {e}")

if __name__ == "__main__":
    debug_rag()
