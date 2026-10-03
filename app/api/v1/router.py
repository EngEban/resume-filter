# ============================================================
# app/api/v1/router.py
# Aggregate all v1 routers.
# ============================================================
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.b2b.analytics import router as b2b_analytics_router
from app.api.v1.b2b.batches import router as b2b_batches_router
from app.api.v1.b2b.results import router as b2b_results_router
from app.api.v1.b2b.settings import router as b2b_settings_router
from app.api.v1.b2c.analyze import router as b2c_analyze_router
from app.api.v1.b2c.history import router as b2c_history_router
from app.api.v1.health import router as health_router

api_router = APIRouter()

# ---------- Health (no auth required) ----------
api_router.include_router(health_router)

# ---------- Authentication ----------
api_router.include_router(auth_router)

# ---------- B2C (Individuals) ----------
api_router.include_router(b2c_analyze_router)
api_router.include_router(b2c_history_router)

# ---------- B2B (Organizations) ----------
api_router.include_router(b2b_batches_router)
api_router.include_router(b2b_results_router)
api_router.include_router(b2b_settings_router)
api_router.include_router(b2b_analytics_router)
