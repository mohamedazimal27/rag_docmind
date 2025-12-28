try:
    from langchain.retrievers.multi_query import MultiQueryRetriever
    print("SUCCESS: from langchain.retrievers.multi_query import MultiQueryRetriever")
except ImportError as e:
    print(f"FAILED: langchain.retrievers.multi_query: {e}")

try:
    from langchain.retrievers import MultiQueryRetriever
    print("SUCCESS: from langchain.retrievers import MultiQueryRetriever")
except ImportError as e:
    print(f"FAILED: langchain.retrievers: {e}")

try:
    from langchain_community.retrievers import MultiQueryRetriever
    print("SUCCESS: from langchain_community.retrievers import MultiQueryRetriever")
except ImportError as e:
    print(f"FAILED: langchain_community.retrievers: {e}")
