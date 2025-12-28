import os
import uuid
from typing import List, Dict, Any
import pandas as pd
import pdfplumber
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
try:
    from langchain_core.documents import Document
except ImportError:
    from langchain.schema import Document

# PRD Section 7: Processed with strict constraints
TEXT_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=400,
    chunk_overlap=80,
    length_function=len,
    is_separator_regex=False,
)

def process_file(file_path: str, original_filename: str, user_id: int) -> List[Document]:
    """
    Extracts text from PDF, TXT, CSV, or XLSX and returns a list of LangChain Documents.
    """
    ext = os.path.splitext(file_path)[1].lower()
    docs = []

    try:
        if ext == ".pdf":
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text() or ""
                    if text.strip():
                        docs.append(Document(
                            page_content=text,
                            metadata={
                                "user_id": user_id,
                                "document_name": original_filename,
                                "page_number": i + 1,
                                "source_file": file_path
                            }
                        ))
        
        elif ext == ".txt":
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
                if text.strip():
                     docs.append(Document(
                        page_content=text,
                        metadata={
                            "user_id": user_id,
                            "document_name": original_filename,
                            "page_number": 1,
                            "source_file": file_path
                        }
                    ))

        elif ext in [".csv", ".xlsx", ".xls"]:
            if ext == ".csv":
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)
            
            # Basic cleaning (PRD Section 7: Step 2)
            df.dropna(how="all", inplace=True)
            df = df.fillna("")
            
            # Convert rows to string format for embedding
            # Grouping generic chunks provided by pandas or iterating rows? 
            # PRD implies strictly managing tokens, but for CSV structure retrieval is tricky.
            # Strategy: Convert each row to a string, then chunk normally, 
            # OR typically for RAG on CSV, each row is a doc.
            # Given the constraint of "Text Extraction" then "Chunking", 
            # let's convert the dataframe to a string representation but keep track of rows?
            # Better approach for PRD "Structured Data" section 12 implies Pandas computes, LLM explains.
            # But for RAG retrieval, we need text.
            # Let's simple-serialize 10 rows at a time or just standard text conversion.
            # PRD Section 7 Step 1: "CSV/XLSX -> pandas".
            # PRD Section 12: "Pandas executes computations... No LLM-driven calculations"
            # This implies the RAG part is mostly for finding *context* or explanation?
            # Let's serialize rows into text blocks roughly matching chunk size or just full text.
            # To support "row_range" metadata, we need to manually chunk by rows.
            
            rows_buffer = []
            start_row = 0
            ROWS_PER_BLOCK = 10 # heuristic to fit in 400 tokens vaguely
            
            for index, row in df.iterrows():
                row_str = " | ".join(f"{col}: {val}" for col, val in row.items())
                rows_buffer.append(row_str)
                
                if len(rows_buffer) >= ROWS_PER_BLOCK:
                    text_block = "\n".join(rows_buffer)
                    end_row = index
                    docs.append(Document(
                        page_content=text_block,
                        metadata={
                            "user_id": user_id,
                            "document_name": original_filename,
                            "row_range": f"rows {start_row}-{end_row}",
                            "source_file": file_path
                        }
                    ))
                    rows_buffer = []
                    start_row = index + 1
            
            # Remaining rows
            if rows_buffer:
                text_block = "\n".join(rows_buffer)
                end_row = start_row + len(rows_buffer) - 1
                docs.append(Document(
                        page_content=text_block,
                        metadata={
                            "user_id": user_id,
                            "document_name": original_filename,
                            "row_range": f"rows {start_row}-{end_row}",
                            "source_file": file_path
                        }
                    ))
                    
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    except Exception as e:
        # print(f"Error processing file {file_path}: {e}")
        raise e

    return docs

def chunk_text(documents: List[Document]) -> List[Document]:
    """
    Splits documents into chunks of 400 tokens (approx characters) with overlap.
    Adds unique chunk_id to metadata.
    """
    chunked_docs = TEXT_SPLITTER.split_documents(documents)
    
    for doc in chunked_docs:
        # Generate unique chunk ID (PRD Section 7)
        doc.metadata["chunk_id"] = str(uuid.uuid4())
        
        # Ensure row_range or page_number persists correctly
        # The splitter keeps metadata from source doc.
        pass
        
    return chunked_docs
