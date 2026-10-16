from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(title="AI Meeting Summarizer")

# Allow the Vite dev server (React) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    """Quick check that the server is up and which keys are configured."""
    return {
        "status": "ok",
        "groq_key_set": bool(settings.groq_api_key),
        "anthropic_key_set": bool(settings.anthropic_api_key),
    }
