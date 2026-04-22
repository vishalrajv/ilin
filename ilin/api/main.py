"""FastAPI application setup with CORS, routers, and static files."""

# Developer: Vishal Raj V, Senior Engineer

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
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

templates = Jinja2Templates(directory=str(frontend_dir / "templates"))
templates.env.cache = None  # FIX: Disable broken Jinja2 cache in Starlette 0.38.6+


@app.get("/")
async def serve_frontend(request: Request):
    """Serve the main HTML page."""
    return templates.TemplateResponse(request, "login.html")


@app.get("/admin")
async def serve_admin(request: Request):
    """Serve admin dashboard."""
    return templates.TemplateResponse(request, "admin.html")


@app.get("/chat")
async def serve_chat(request: Request):
    """Serve user chat interface."""
    return templates.TemplateResponse(request, "chat.html")


@app.on_event("startup")
def startup():
    """Initialize database on startup."""
    init_db()
    from ilin.config import settings

    settings.data_dir.mkdir(parents=True, exist_ok=True)
    (settings.data_dir / "documents").mkdir(exist_ok=True)
    (settings.data_dir / "indexes").mkdir(exist_ok=True)
    (settings.data_dir / "models").mkdir(exist_ok=True)
