

---

# 📄 Product Requirements Document (PRD)

## Product Name

**DocuMind Pro**

**Tagline:**
*A fast, source-grounded document Q&A system built with production-grade RAG.*

---

## 1. Objective

Build a **performance-optimized RAG-based Q&A application** that allows authenticated users to upload documents and ask natural-language questions, receiving **accurate answers with verifiable sources**, while operating reliably on a **low-spec laptop (4 GB RAM)** using a **maximum $5 API budget**.

The product must demonstrate **real-world AI engineering judgment**, not just LLM usage.

---

## 2. Key Constraints (Hard Rules)

* Laptop RAM: **4 GB**
* No local LLM inference
* API spend: **≤ $5**
* Response time target: **< 3 seconds**
* One clear framework: **LangChain**
* No experimental or agent-based features

---

## 3. Target Users

* Individual professionals
* Students and researchers
* Recruiters and hiring managers evaluating AI systems
* Freelancers demonstrating applied AI skills

---

## 4. Tech Stack (FINAL)

### Backend

* **Python**
* **FastAPI**
* **LangChain** (RAG orchestration only)

### Frontend

* **React (Vite)**
* Simple, minimal UI

### LLM

* **OpenAI `gpt-4o-mini`**

### Embeddings

* **OpenAI `text-embedding-3-small`**

### Vector Database

* **ChromaDB (local, persistent)**

### Storage

* Local filesystem

---

## 5. Authentication & User Isolation

### Requirements

* Email + password authentication
* JWT-based authorization
* Each user has:

  * A dedicated upload directory
  * A dedicated ChromaDB collection
* Backend enforces strict user-level isolation

### Out of Scope

* OAuth
* Teams
* Roles

---

## 6. Document Upload & Limits

### Supported File Types

* PDF
* TXT
* CSV
* XLSX

### Hard Limits

* Max file size: **5 MB**
* Max files per user: **15**
* Total embedded chunks per user: capped to prevent cost overrun

### UI Requirements

* Upload progress indicator
* Clear success / failure messages
* List and delete uploaded files

---

## 7. Document Processing Pipeline

### Step 1: Text Extraction

* PDF → `pdfplumber`
* TXT → native read
* CSV/XLSX → `pandas`

### Step 2: Cleaning

* Remove headers, footers, empty rows
* Normalize whitespace

### Step 3: Chunking (Performance-Tuned)

* Chunk size: **400 tokens**
* Overlap: **80 tokens**
* LangChain `RecursiveCharacterTextSplitter`

### Step 4: Metadata (Mandatory)

Each chunk must include:

* `user_id`
* `document_name`
* `page_number` OR `row_range`
* `chunk_id`

---

## 8. Embedding Strategy

* Embeddings generated **once at upload**
* Batched embedding requests
* Stored persistently in ChromaDB
* Duplicate content is never re-embedded

**Cost target:** < $1 total

---

## 9. Retrieval Strategy

* Top-k retrieval: **k = 4**
* Metadata filtering by `user_id`
* No reranking in v1 (latency-first design)

---

## 10. RAG Pipeline (LangChain)

### Flow

1. User submits question
2. Question embedded
3. Relevant chunks retrieved from ChromaDB
4. Context injected into prompt
5. `gpt-4o-mini` generates answer
6. Sources returned with answer

### Grounding Rules

* Model may ONLY use retrieved context
* If answer not found → explicit refusal

---

## 11. Answer Format (Strict)

```
Answer:
<concise, grounded response>

Sources:
- File: <document_name> | Page/Rows: <reference>
```

Hallucinated content is considered a **hard failure**.

---

## 12. Structured Data Handling (CSV / XLSX)

### Supported Operations

* Sum
* Average
* Count
* Top-N
* Column-based filtering

### Execution Model

* Pandas executes computations
* LLM explains results only
* No LLM-driven calculations

This minimizes token usage and errors.

---

## 13. Chat Interface Requirements

### Must Display

* User question
* Assistant answer
* Source citations
* Timestamp
* Chat history per user

### Must Not Include

* Streaming responses
* Voice input
* Images
* Web browsing

---

## 14. Performance Targets

* Vector retrieval: **< 200 ms**
* End-to-end Q&A latency: **< 3 seconds**
* Upload processing handled asynchronously

---

## 15. Security Requirements

* API keys stored in `.env`
* Uploaded files never publicly accessible
* User queries restricted to their own data
* No cross-user vector access

---

## 16. Explicitly Out of Scope (v1)

* Agents
* Tool calling
* Web scraping
* SaaS billing
* Multimodal input
* Fine-tuning
* Docker / Kubernetes

---

## 17. Success Criteria

The product is considered successful if:

* Users can upload documents reliably
* Ask questions and receive accurate answers
* Every answer includes verifiable sources
* App runs smoothly on a 4 GB RAM system
* API spend remains under $5

---

## 18. Recruiter Signal Summary

This PRD demonstrates:

* Cost-aware AI engineering
* RAG grounding and safety
* Performance-first design
* Clear architectural decisions
* Production-level thinking

---

## 19. Versioning

### v1 (This PRD)

* Single-user knowledge assistant
* Local deployment
* Budget-controlled RAG

### v2 (Future, Not Implemented)

* Cloud hosting
* Team workspaces
* Usage analytics

---
