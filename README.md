# 🚀 Brand Guardian AI

### Azure Multimodal Compliance Orchestration Engine

---

## 📌 Overview

**Brand Guardian AI** is a production-grade **AI-powered compliance auditing system** that analyzes video content (e.g., ads, influencer promotions) and evaluates whether it adheres to regulatory guidelines (such as FTC rules).

The system leverages:

* LangGraph for workflow orchestration
* FastAPI for backend APIs
* Azure OpenAI Service for reasoning
* Azure AI Search for retrieval
* Azure Video Indexer for multimodal extraction
* LangSmith for tracing and debugging

---

## 🎯 Problem Statement

Brands publish large volumes of video content, but ensuring **regulatory compliance** is:

* ❌ Manual and time-consuming
* ❌ Hard to scale
* ❌ Prone to human error

### ✅ Solution

Automate compliance auditing by:

1. Extracting **transcript + OCR text** from videos
2. Retrieving **relevant regulatory rules**
3. Using an LLM to **detect violations**
4. Generating a **structured compliance report**

---

## 🧠 Key Features

* 🎥 **Multimodal Processing** (Video → Transcript + OCR)
* 📚 **RAG-based Compliance Checking**
* 🤖 **LLM-Powered Reasoning (GPT-4o)**
* 🔄 **Agentic Workflow (LangGraph)**
* 🌐 **Production API (FastAPI)**
* 📊 **Observability (Azure Monitor + LangSmith)**

---

## 🏗️ Architecture

```text
User Input (YouTube URL)
        ↓
FastAPI Backend
        ↓
LangGraph Workflow
   ├── Video Indexer (Azure)
   ├── Data Extraction (Transcript + OCR)
   ├── Retrieval (Azure AI Search)
   └── LLM Audit (GPT-4o)
        ↓
Compliance Report (PASS / FAIL)
```

---

## 🔄 End-to-End Workflow

### 1. Input

* User submits a **YouTube URL**

### 2. Video Processing

* Download video using `yt-dlp`
* Upload to Azure Video Indexer
* Extract:

  * Transcript (speech)
  * OCR text (on-screen content)

### 3. Knowledge Retrieval (RAG)

* Regulatory documents are:

  * Chunked
  * Embedded
  * Stored in Azure AI Search

* At runtime:

  * Relevant rules are retrieved via **semantic search**

### 4. LLM Reasoning

* Inputs:

  * Transcript
  * OCR text
  * Retrieved rules

* Output:

  * Violations
  * Severity
  * Final report

### 5. Output

* Structured compliance report:

  * ✅ PASS / ❌ FAIL
  * Detailed violations
  * Natural language summary

---

## 📦 Tech Stack

| Layer            | Technology                |
| ---------------- | ------------------------- |
| Backend API      | FastAPI                   |
| Orchestration    | LangGraph                 |
| LLM              | Azure OpenAI (GPT-4o)     |
| Embeddings       | Azure OpenAI              |
| Vector DB        | Azure AI Search           |
| Video Processing | Azure Video Indexer       |
| Observability    | Azure Monitor + LangSmith |
| Data Processing  | LangChain                 |

---

## 📁 Project Structure

```bash
backend/
├── src/
│   ├── api/
│   │   ├── server.py        # FastAPI backend
│   │   └── telemetry.py     # Observability setup
│   │
│   ├── graph/
│   │   ├── workflow.py      # LangGraph DAG
│   │   ├── nodes.py         # Core logic (Indexer + Auditor)
│   │   └── state.py         # Shared state schema
│   │
│   ├── services/
│   │   └── video_indexer.py # Azure Video Indexer integration
│
├── data/                    # Regulatory PDFs
│
scripts/
└── index_documents.py       # RAG knowledge base creation

.env                         # Environment variables
main.py                      # CLI runner
```

---

## ⚙️ Setup & Installation

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd brand-guardian-ai
```

---

### 2. Install Dependencies

```bash
uv sync
```

---

### 3. Configure Environment Variables

Create a `.env` file:

```env
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=...
AZURE_SEARCH_ENDPOINT=...
AZURE_SEARCH_API_KEY=...
AZURE_VI_ACCOUNT_ID=...
AZURE_MONITOR_CONNECTION_STRING=...
LANGCHAIN_API_KEY=...
```

---

### 4. Index Documents (RAG Setup)

```bash
python scripts/index_documents.py
```

---

### 5. Run API Server

```bash
uv run uvicorn backend.src.api.server:app --reload
```

---

### 6. Test API

```http
POST /audit
```

```json
{
  "video_url": "https://youtu.be/your-video"
}
```

---

## 📊 Sample Output

```json
{
  "status": "FAIL",
  "compliance_results": [
    {
      "category": "Misleading Claims",
      "severity": "CRITICAL",
      "description": "Absolute guarantee detected"
    }
  ],
  "final_report": "Video contains critical compliance violations..."
}
```

---

## 🧩 Core Components Explained

### 🔹 Indexer Node

* Downloads video
* Uploads to Azure
* Extracts transcript + OCR

### 🔹 Auditor Node

* Performs RAG:

  * Retrieves rules
  * Calls LLM
* Generates structured output

### 🔹 LangGraph Workflow

* Orchestrates:

  * Indexer → Auditor
* Maintains shared state

---

## 📡 Observability

* Tracks:

  * API latency
  * Errors
  * LLM calls
* Tools:

  * Azure Monitor
  * LangSmith

---

## 🚀 Key Highlights (For Recruiters)

* ✅ End-to-end LLM system (not a toy project)
* ✅ RAG pipeline with Azure AI Search
* ✅ Multimodal AI (video + OCR + text)
* ✅ Agentic workflow (LangGraph)
* ✅ Production backend (FastAPI)
* ✅ Observability & monitoring
* ✅ Cloud-native architecture

---

## 🎯 Future Improvements

* Add async execution (`ainvoke`)
* Stream processing for long videos
* Real-time dashboard UI
* Multi-language compliance support
* Batch video auditing

---

## 🧠 Author

**Gautham N Vijayan**
Aspiring AI Engineer | Building production-grade GenAI systems

---

## ⭐ If you found this useful

Give this repo a ⭐ and feel free to connect!

