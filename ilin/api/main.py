"""FastAPI application setup with CORS, routers, and static files."""

# Developer: Vishal Raj V, Senior Engineer

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from ilin.storage.database import init_db
from ilin.api.auth_router import router as auth_router
from ilin.api.admin_router import router as admin_router
from ilin.api.chat_router import router as chat_router


app = FastAPI(title="ILIN", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(chat_router)

frontend_dir = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(frontend_dir / "static")), name="static")


@app.get("/")
async def serve_frontend():
    """Serve the main HTML page."""
    return FileResponse(str(frontend_dir / "templates" / "login.html"))


@app.get("/admin")
async def serve_admin():
    """Serve admin dashboard."""
    return FileResponse(str(frontend_dir / "templates" / "admin.html"))


@app.get("/chat")
async def serve_chat():
    """Serve user chat interface."""
    return FileResponse(str(frontend_dir / "templates" / "chat.html"))


@app.on_event("startup")
def startup():
    """Initialize database on startup."""
    init_db()
    from ilin.config import settings

    settings.data_dir.mkdir(parents=True, exist_ok=True)
    (settings.data_dir / "documents").mkdir(exist_ok=True)
    (settings.data_dir / "indexes").mkdir(exist_ok=True)
    (settings.data_dir / "models").mkdir(exist_ok=True)
