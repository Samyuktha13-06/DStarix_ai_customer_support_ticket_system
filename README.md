# AI Customer Support & Ticket Automation System

An AI-powered customer support system that combines:

- Retrieval-Augmented Generation (RAG)
- AI agents
- Tool calling
- Conversation memory
- Human escalation
- FastAPI
- LangChain
- LangGraph
- Groq LLM
- Vector database
- Application database

## Current Status

Phase 1 - Project setup and backend foundation.

## Technology Stack

- Python
- FastAPI
- Groq
- LangChain
- LangGraph
- SQLAlchemy
- SQLite
- ChromaDB
- Pytest

## Running the Application

```bash
pip install -r requirements.txt


## RAG Architecture

The system uses Retrieval-Augmented Generation to answer
NovaCart-specific questions using the company's knowledge base.

The current RAG pipeline consists of:

1. Knowledge-base documents
2. LangChain document loading
3. Recursive text splitting
4. Local Hugging Face embeddings
5. ChromaDB vector storage
6. Semantic similarity retrieval

The generation component will be integrated with the
Groq LLM in the next phase.

### Embedding Model

The project currently uses:

`sentence-transformers/all-MiniLM-L6-v2`

The embedding model runs locally and does not require an
external embedding API call.

### Vector Database

ChromaDB is used as the persistent vector store.

Generated Chroma data is excluded from Git because it can
be recreated from the source knowledge-base documents.

### Source Tracking

Each chunk stores metadata including:

- Source filename
- File path
- File type
- Chunk ID