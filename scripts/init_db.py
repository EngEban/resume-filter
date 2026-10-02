# ============================================================
# scripts/init_db.py
# Create all tables (dev shortcut; use Alembic for prod).
# ============================================================
import asyncio
import logging

from app.db.base import Base
from app.db.models import Analysis, Batch, Resume, Tenant, User  # noqa: F401
from app.db.session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("All tables created.")


def main() -> None:
    asyncio.run(create_tables())


if __name__ == "__main__":
    main()