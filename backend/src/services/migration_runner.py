"""
Migration Runner

Docker 환경에서 SQLite → PostgreSQL 마이그레이션 실행
"""

import asyncio
import os
import sys

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from .migration import MigrationService


async def run_migration():
    """마이그레이션 실행"""
    # Get configuration from environment
    postgres_host = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port = os.getenv("POSTGRES_PORT", "5432")
    postgres_user = os.getenv("POSTGRES_USER", "wsoptv")
    postgres_password = os.getenv("POSTGRES_PASSWORD", "")
    postgres_db = os.getenv("POSTGRES_DB", "wsoptv")
    sqlite_path = os.getenv("SQLITE_PATH", "/data/pokervod.db")

    database_url = f"postgresql+asyncpg://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

    print(f"[Migration] Connecting to PostgreSQL at {postgres_host}:{postgres_port}")
    print(f"[Migration] SQLite source: {sqlite_path}")

    # Create engine and session
    engine = create_async_engine(database_url, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create migration service
    migration_service = MigrationService(sqlite_path=sqlite_path)

    try:
        async with async_session() as session:
            print("[Migration] Starting migration...")
            results = await migration_service.migrate_all(session)

            print("\n" + "=" * 50)
            print("[Migration] Results:")
            print("=" * 50)
            for table, count in results.items():
                print(f"  {table}: {count} records")
            print("=" * 50)
            print("[Migration] Completed successfully!")

    except FileNotFoundError as e:
        print(f"[Migration] ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[Migration] ERROR: {e}")
        sys.exit(1)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(run_migration())
