# TTRPG Session Ledger Microservice

A modular microservice built with FastAPI, LangChain, and Google Gemini. This service ingests unstructured Game Master notes from tabletop roleplaying sessions, utilizes a LLM to extract structured entities (NPCs, locations, items) and unresolved narrative hooks, and persists the state asynchronously to a SQLite database.

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