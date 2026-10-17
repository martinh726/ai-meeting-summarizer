from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.db import create_db_and_tables
from app.routers import meetings


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="AI Meeting Summarizer", lifespan=lifespan)

# Allow the Vite dev server (React) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meetings.router)


@app.get("/health")
def health():
    """Quick check that the server is up and which keys are configured."""
    return {
        "status": "ok",
        "groq_key_set": bool(settings.groq_api_key),
        "anthropic_key_set": bool(settings.anthropic_api_key),
    }
