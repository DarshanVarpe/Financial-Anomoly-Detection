# backend/app/main.py — FraudOS FastAPI entry point
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os

from app.config import CORS_ORIGIN
from app.db.pool import lifespan
from app.routers import dashboard, transactions, model, reports

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="FraudOS API",
    description="AI-Powered Fraud Detection — CentificAI Aegis",
    version="2.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ─────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGIN] if CORS_ORIGIN != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# ── Routers ───────────────────────────────────────────────────
app.include_router(dashboard.router,    prefix="/rahul-aegis/dashboard",     tags=["dashboard"])
app.include_router(transactions.router, prefix="/rahul-aegis/transactions",  tags=["transactions"])
app.include_router(model.router,        prefix="/rahul-aegis/model",         tags=["model"])
app.include_router(reports.router,      prefix="/rahul-aegis/reports",       tags=["reports"])

# ── Health ────────────────────────────────────────────────────
@app.get("/rahul-aegis/health", tags=["health"])
async def health():
    from datetime import datetime, timezone
    return {
        "status": "ok",
        "service": "FraudOS API",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
