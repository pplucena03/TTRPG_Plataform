# TTRPG Session Ledger Microservice

A modular microservice built with FastAPI, LangChain, and Google Gemini. This service ingests unstructured Game Master notes from tabletop roleplaying sessions, utilizes a Large Language Model to extract structured entities (NPCs, locations, items) and unresolved narrative hooks, and persists the state asynchronously to a SQLite database.

## Architecture & Tech Stack
* **Framework:** FastAPI (Asynchronous)
* **AI/LLM:** Google Gemini 3.7 Flash via LangChain
* **Telemetry & Evaluation:** LangSmith
* **Database:** SQLite with SQLAlchemy 2.0 (aiosqlite)
* **Migrations:** Alembic
* **Data Validation:** Pydantic

## Prerequisites
* Python 3.10+
* Google Gemini API Key
* LangSmith API Key (for prompt versioning and tracing)

## Setup & Installation

1. **Initialize the Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_gemini_key_here
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_langsmith_key_here
   LANGCHAIN_PROJECT=session-ledger-v1
   ```

4. **Initialize the Database**
   Run the Alembic migrations to generate the SQLite database and schemas:
   ```bash
   alembic upgrade head
   ```

## Running the Service

Start the ASGI server using Uvicorn:
```bash
uvicorn app.main:app --reload --port 8000
```
* Interactive API Documentation (Swagger UI) is available at: `http://127.0.0.1:8000/docs`

## Automated LLM Evaluation

This service includes an offline evaluation suite to benchmark the LLM's entity extraction capabilities against ground-truth datasets.
```bash
python evaluate_pipeline.py
```
*Results, including latency and entity recall scores, are pushed directly to the LangSmith dashboard.*