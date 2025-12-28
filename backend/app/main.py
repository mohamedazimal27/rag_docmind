import os
import shutil
from pathlib import Path
from typing import List

from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .database import engine, Base
from . import auth, models, ingest, vector_store, schemas

# Create Database Tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="DocuMind Pro Backend")

# Configuration (Same as auth.py, centralized would be better but keeping simple)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

# CORS (Allow frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["Authentication"])

@app.get("/")
def read_root():
    return {"message": "DocuMind Pro API is running"}

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: models.User = Depends(auth.get_current_user) # We need to expose a get_current_user in auth
):
    user_id = current_user.id
    user_files_dir = DATA_DIR / str(user_id) / "files"
    
    # Ensure directory exists
    os.makedirs(user_files_dir, exist_ok=True)
    
    # 1. Enforce Max Files Limit (PRD: Max 15)
    existing_files = [f for f in os.listdir(user_files_dir) if os.path.isfile(os.path.join(user_files_dir, f))]
    if len(existing_files) >= 15:
         raise HTTPException(status_code=400, detail="File limit exceeded (Max 15 files). Delete some files to upload more.")

    # 2. Save File
    file_path = user_files_dir / file.filename
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")
        
    # 3. Process & Ingest
    try:
        # Extract
        raw_docs = ingest.process_file(str(file_path), file.filename, user_id)
        
        # Chunk
        chunks = ingest.chunk_text(raw_docs)
        
        # Embed & Store
        vector_store.add_documents_to_chroma(user_id, chunks)
        
        return {
            "filename": file.filename,
            "status": "success",
            "chunks_processed": len(chunks),
            "total_files": len(existing_files) + 1
        }
        
    except ValueError as e:
         # Cleanup invalid file
         os.remove(file_path)
         raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
         # Cleanup on failure
         if os.path.exists(file_path):
            os.remove(file_path)
         print(f"Ingestion failed: {e}")
         raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

