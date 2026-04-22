# AGENTS.md - ILIN Repository
# Developer: Vishal Raj V, Senior Engineer

---

## Repository Overview
- Python 3.10+ FastAPI + SQLAlchemy web application
- RAG / document processing system with FAISS vector store
- Standard Python package layout: `ilin/` is main module

---

## Verified Commands
```powershell
# Setup
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run application
python run.py

# Initialize database / seed admin user
python seed.py

# Run tests
pytest

# Lint
ruff check .
```

---

## Project Structure
```
ilin/
├── api/          # FastAPI routes, main app entrypoint at api/main.py
├── auth/         # Authentication logic
├── core/         # Business logic, RAG pipelines
├── frontend/     # Jinja2 templates, static assets
├── storage/      # SQLAlchemy models, database operations
└── config.py     # Pydantic environment settings
```

---

## Conventions & Rules
1. **Always use pathlib.Path() for file paths - never os.path**
2. Use f-strings for all string formatting
3. Catch only specific exceptions - never bare `except:`
4. Small single-purpose functions with one-line docstrings
5. No raw SQL - use SQLAlchemy ORM exclusively
6. All terminal commands assume Windows PowerShell
7. Never install packages globally - always use .venv

---

## Important Gotchas
- Ruff is used for linting (cache present, no config file yet)
- Tests use pytest with fixtures in `tests/conftest.py`
- Environment variables loaded via Pydantic Settings from `.env`
- No CI workflows configured currently
- No custom task runners - use standard commands above

---

## Workflow
For any task with 3+ steps:
1. Write plan to `tasks/todo.md` first
2. Verify plan before implementation
3. Track progress with checkboxes
4. Always verify code runs before marking complete
5. After corrections, update `tasks/lessons.md`
