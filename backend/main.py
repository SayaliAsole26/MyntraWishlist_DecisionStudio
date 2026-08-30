import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend import config  # noqa: F401  — loads .env
from backend.api.routes.alerts import router as alerts_router
from backend.api.routes.bag import router as bag_router
from backend.api.routes.checkout import router as checkout_router
from backend.api.routes.health import router as health_router
from backend.api.routes.products import router as products_router
from backend.api.routes.profile import router as profile_router
from backend.api.routes.questions import router as questions_router
from backend.api.routes.wishlist import router as wishlist_router
from backend.db.init_db import init_database

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_database()
    yield


app = FastAPI(
    title="Myntra Wishlist Decision Studio",
    description="Phase 6 — Polish, mock checkout, demo-ready MVP. Wishlist GET stays Groq-free.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(products_router)
app.include_router(wishlist_router)
app.include_router(alerts_router)
app.include_router(bag_router)
app.include_router(checkout_router)
app.include_router(profile_router)
app.include_router(questions_router)
