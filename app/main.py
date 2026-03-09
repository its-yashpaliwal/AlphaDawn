"""
FastAPI application entry-point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.config import settings
from app.api.routes import picks, news, feedback, signals, pipeline, paper_trade


# ── Lifespan ────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀  AlphaDawn starting up …")
    # TODO: initialise DB pool, Redis connection, scheduler
    yield
    logger.info("👋  AlphaDawn shutting down …")


# ── App instance ────────────────────────────────────────────────────────────
app = FastAPI(
    title="AlphaDawn",
    description="AI-powered pre-market intelligence for Indian stock markets",
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS ────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ──────────────────────────────────────────────────────────────────
app.include_router(picks.router, prefix="/api/v1", tags=["Picks"])
app.include_router(news.router, prefix="/api/v1", tags=["News"])
app.include_router(feedback.router, prefix="/api/v1", tags=["Feedback"])
app.include_router(signals.router, prefix="/api/v1", tags=["Signals"])
app.include_router(pipeline.router, prefix="/api/v1/pipeline", tags=["Pipeline"])
app.include_router(paper_trade.router, prefix="/api/v1/paper-trade", tags=["Paper Trading"])


@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "env": settings.app_env}
