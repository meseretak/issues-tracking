from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
import os

from app.database import init_db
from app.routers import auth, users, projects, issues, comments, sprints, dashboard, notifications, reports, teams, workflow, chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title="Awash Bank Issue Tracker",
    description="Enterprise-grade project & issue management for Awash Bank",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers ───────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(issues.router)
app.include_router(comments.router)
app.include_router(sprints.router)
app.include_router(dashboard.router)
app.include_router(notifications.router)
app.include_router(reports.router)
app.include_router(teams.router)
app.include_router(workflow.router)
app.include_router(chat.router)

# ── Frontend ──────────────────────────────────────────────────────────────────
frontend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))


@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse(os.path.join(frontend_path, "index.html"), media_type="text/html")


@app.get("/app.css", include_in_schema=False)
async def serve_css():
    return FileResponse(os.path.join(frontend_path, "app.css"), media_type="text/css")


@app.get("/app.js", include_in_schema=False)
async def serve_js():
    return FileResponse(os.path.join(frontend_path, "app.js"), media_type="application/javascript")
