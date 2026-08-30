"""Project configuration loaded from .env."""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent

load_dotenv(ROOT_DIR / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
GROQ_MODEL_FAST = os.getenv("GROQ_MODEL_FAST", "openai/gpt-oss-20b")
GROQ_MODEL_QUALITY = os.getenv("GROQ_MODEL_QUALITY", "openai/gpt-oss-120b")
GROQ_TIMEOUT = float(os.getenv("GROQ_TIMEOUT", "30"))

# SQLite — override on Railway if using a mounted volume path
DATABASE_PATH = os.getenv("DATABASE_PATH", "").strip()

# Comma-separated browser origins for CORS (include production frontend URL)
_default_cors = "http://localhost:5173,http://127.0.0.1:5173"
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", _default_cors).split(",")
    if o.strip()
]
