# Tech Stack: ILIN

## Core Language & Frameworks
- **Python 3.10+**: The primary programming language.
- **FastAPI**: The core backend framework, served via Uvicorn, providing high performance and auto-generated API documentation.

## Database & Storage
- **SQLAlchemy**: The ORM used for all relational database interactions.
- **FAISS (CPU)**: Vector store used for the RAG engine's similarity search.

## AI & RAG Components
- **sentence-transformers**: For generating text embeddings.
- **llama-cpp-python**: For local LLM inference capabilities.
- **OpenAI**: Client library for optional cloud-based LLM integration.
- Document processing tools including `PyMuPDF`, `python-docx`, `python-pptx`, and `openpyxl`.

## Frontend
- **Jinja2**: Server-side HTML templating engine.
- **Alpine.js & Chart.js**: For lightweight client-side reactivity and data visualization in the admin dashboard.
- **Vanilla HTML/CSS/JS**: Core client-side structure and styling.

## Authentication & Security
- **PyJWT & bcrypt**: Used for secure token generation and password hashing.

## Testing & Quality Assurance
- **pytest**: The testing framework.
- **ruff**: Linter for ensuring code quality.