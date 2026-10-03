"""Drop all tables and re-run Alembic migrations (development only)."""
import asyncio
import logging
import subprocess
import sys

from sqlalchemy import text

from app.db.session import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


DROP_ALL_SQL = """
DO $$ DECLARE
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END $$;
"""


async def drop_all_tables() -> None:
    async with engine.begin() as conn:
        await conn.execute(text(DROP_ALL_SQL))
    logger.info("All tables dropped.")


def run_migrations() -> None:
    logger.info("Running Alembic migrations...")
    subprocess.run(
        ["alembic", "upgrade", "head"],
        check=True,
    )
    logger.info("Migrations applied.")


def main() -> None:
    confirm = input("This will DELETE ALL DATA. Continue? (yes/no): ")
    if confirm.strip().lower() != "yes":
        print("Aborted.")
        sys.exit(1)

    asyncio.run(drop_all_tables())
    run_migrations()
    print("Database reset complete.")


if __name__ == "__main__":
    main()
