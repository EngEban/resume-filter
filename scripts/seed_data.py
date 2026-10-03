"""Seed the database with a default tenant for development."""

import asyncio
import logging

from sqlalchemy import select

from app.db.models.tenant import Tenant
from app.db.session import get_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DEFAULT_TENANT_ID = "00000000-0000-0000-0000-000000000001"


async def seed() -> None:
    async with get_session() as session:
        existing = await session.execute(select(Tenant).where(Tenant.slug == "default"))
        if existing.scalar_one_or_none():
            logger.info("Default tenant already exists.")
            return

        tenant = Tenant(
            id=DEFAULT_TENANT_ID,
            name="Default Tenant",
            slug="default",
            plan="free",
        )
        session.add(tenant)
        await session.commit()
        logger.info("Created default tenant.")


def main() -> None:
    asyncio.run(seed())


if __name__ == "__main__":
    main()
