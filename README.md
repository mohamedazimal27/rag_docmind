# DocuMind Pro

DocuMind Pro is a RAG-based (Retrieval Augmented Generation) Document Q&A application. It allows users to upload documents (PDF, TXT, CSV) and ask questions about them using an LLM, with strict data isolation per user.

## Features
- **User Authentication**: Secure Signup/Login (JWT-based).
- **Document Ingestion**: Supports PDF, TXT, and CSV/XLSX.
- **RAG Pipeline**: 
  - Chunking & Embedding (OpenAI).
  - Vector Storage (ChromaDB) with user isolation.
  - Retrieval (Top-k similarity search).
- **Chat Interface**: Interactive UI asking questions and viewing sources.

## Prerequisites
- **Python 3.10+**
- **Node.js** & **npm**
- **OpenAI API Key**

## Installation

### 1. Backend Setup
Navigate to the project root:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup
Navigate to the frontend directory:
```bash
cd frontend
npm install
cd ..
```

### 3. Environment Variables
Create a `.env` file in the **project root** directory (`/home/mohamed-azimal/code/n8n-codes/RAG/portfolio_project/.env`):

```bash
OPENAI_API_KEY=sk-...your_key_here...
SECRET_KEY=your_secure_secret_key
```

## Running the Application

You need to run the backend and frontend in separate terminals.

### Terminal 1: Backend
```bash
# From project root
source venv/bin/activate
uvicorn backend.app.main:app --reload --port 8000
```
*The API will be available at http://localhost:8000*
*Swagger Docs: http://localhost:8000/docs*

### Terminal 2: Frontend
```bash
# From project root
cd frontend
npm run dev
```
*The App will be running at http://localhost:5173*

## Usage Guide to Test
1.  **Open App**: Go to [http://localhost:5173](http://localhost:5173).
2.  **Login**: Use credentials `test@example.com` / `securepassword`.
    *   *(Note: Registration API exists at `/register` but UI currently only has Login. Use Swagger UI to register new users if needed).*
3.  **Upload**: Click the "Upload Document" button and select a file.
4.  **Chat**: Type a question like "Summarize this document" or "What does the file say about X?".

## Project Structure
- `backend/app`: FastAPI application source code.
- `frontend/src`: React application source code.
- `data/`: Stores user files and ChromaDB vectors (created automatically).
