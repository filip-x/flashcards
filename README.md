# FastAPI Smart Flashcards

A robust, async-first FastAPI backend that generates AI-powered flashcards from uploaded documents (PDF, TXT, Markdown) and manages spaced repetition reviews using the **SM-2 algorithm**.

## Features
- **File Parsing**: Upload PDFs, TXT, or Markdown documents. Extracts raw text efficiently.
- **Smart Chunking**: Splits large documents into overlapping context windows suitable for LLM processing.
- **AI Generation**: Integrates with OpenAI (`gpt-4o-mini`) via structured JSON output to deterministically generate high-quality active recall flashcards.
- **Deduplication & Validation**: Validates AI JSON output formats and deduplicates questions.
- **Spaced Repetition (SM-2)**: Implements the SuperMemo-2 algorithm. When a user reviews a card (quality 0–5), the backend recalculates their precise ease factor, interval, and next due date.
- **Async Database Layer**: Full async integration with PostgreSQL 16 via SQLAlchemy 2.0 + `asyncpg`.
- **Alembic Migrations**: Fully configured for async schema management.

## Project Structure
```text
.
├── alembic/              # Database migrations
├── app/
│   ├── models/           # SQLAlchemy ORM models (Document, Flashcard, Review)
│   ├── routers/          # FastAPI routers
│   ├── schemas/          # Pydantic validation schemas
│   ├── services/         # Core business logic (OpenAI, SM-2, Chunker, Parser)
│   ├── config.py         # pydantic-settings config
│   ├── database.py       # Async SQLAlchemy engine
│   └── main.py           # FastAPI application entrypoint
├── tests/                # Comprehensive unit & integration suite using aiosqlite
├── docker-compose.yml    # Development PostgreSQL service
├── requirements.txt      # Dependencies
└── pyproject.toml        # Tool configuration (pytest, mypy)
```

## Running the Application

### 1. Requirements
- Python 3.11+
- Docker & Docker Compose (for PostgreSQL)
- OpenAI API Key

### 2. Setup
```bash
# Clone the repository
git clone <repo-url>
cd flashcards

# Set up a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Copy the template to create a `.env` file and insert your API key:
```bash
cp .env.example .env
# Edit .env and replace sk-your-key-here with a real OpenAI key
```

### 4. Database Initialization
```bash
# Start the local database
docker-compose up -d

# Run migrations (creates tables)
alembic upgrade head
```

### 5. Start the Server
```bash
uvicorn app.main:app --reload
```

Then visit the interactive Swagger API documentation at:
**[http://localhost:8000/docs](http://localhost:8000/docs)**

## Running Tests
An extensive test suite covering the SM-2 algorithm, string parsing, chunking, deduplication, and integration endpoints (using an in-memory `aiosqlite` test DB).

```bash
pytest tests/ -v
```
