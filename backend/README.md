# PayPilot Backend

FastAPI service powering PayPilot, the AI commerce agent.

## Features
- **FastAPI** web framework with automatic OpenAPI docs (`/docs`)
- **Pydantic Settings** environment configuration
- **SQLAlchemy** ready for PostgreSQL database storage
- **Pytest** automated testing suite
- Clean modular structure (`api`, `core`, `models`, `schemas`, `services`)

## Directory Layout
```text
backend/
├── app/
│   ├── api/          # API endpoints & routing
│   ├── core/         # Settings, database connection & configs
│   ├── models/       # SQLAlchemy database models
│   ├── schemas/      # Pydantic schemas for request/response validation
│   ├── services/     # Business logic & services
│   └── main.py       # FastAPI application factory & root router
├── tests/            # Test suite
├── requirements.txt  # Dependencies
└── README.md
```

## Quickstart

### 1. Create and Activate Virtual Environment
```bash
python -m venv .venv
# On Windows:
.venv\Scripts\Activate.ps1
# On macOS/Linux:
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Development Server
```bash
uvicorn app.main:app --reload --port 8000
```

### 4. Interactive Documentation
Open http://127.0.0.1:8000/docs in your browser.

### 5. Run Tests
```bash
pytest
```
