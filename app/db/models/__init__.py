# ============================================================
# app/db/models/__init__.py
# Import all models here so Alembic can detect them.
# ============================================================
from app.db.models.tenant import Tenant
from app.db.models.user import User
from app.db.models.batch import Batch
from app.db.models.resume import Resume
from app.db.models.analysis import Analysis

__all__ = [
    "Tenant",
    "User",
    "Batch",
    "Resume",
    "Analysis",
]