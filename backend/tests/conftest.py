"""
WSOPTV Test Configuration

This module provides pytest fixtures for isolated test environment.
CRITICAL: Tests MUST use test database, never production.
"""

import os
import pytest
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from httpx import AsyncClient, ASGITransport

# Force test environment BEFORE importing app modules
os.environ["TESTING"] = "true"
os.environ["POSTGRES_HOST"] = "localhost"
os.environ["POSTGRES_PORT"] = "5434"  # Test DB port
os.environ["POSTGRES_USER"] = "wsoptv_test"
os.environ["POSTGRES_PASSWORD"] = "test_password_only"
os.environ["POSTGRES_DB"] = "wsoptv_test"
os.environ["REDIS_HOST"] = "localhost"
os.environ["REDIS_PORT"] = "6380"  # Test Redis port
os.environ["MEILI_HOST"] = "http://localhost:7701"  # Test MeiliSearch port
os.environ["MEILI_MASTER_KEY"] = "test_meili_key_only"
os.environ["JWT_SECRET_KEY"] = "test_jwt_secret_key_only"

# Now import app modules
from src.main import app
from src.core.database import Base, get_db
from src.models import User
from src.core.security import get_password_hash


# Test Database URL
TEST_DATABASE_URL = (
    f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
    f"@{os.environ['POSTGRES_HOST']}:{os.environ['POSTGRES_PORT']}/{os.environ['POSTGRES_DB']}"
)

TEST_DATABASE_URL_ASYNC = TEST_DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine (sync for setup)."""
    engine = create_engine(TEST_DATABASE_URL)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def test_async_engine():
    """Create test database engine (async)."""
    engine = create_async_engine(TEST_DATABASE_URL_ASYNC, echo=False)
    yield engine


@pytest.fixture(scope="function")
def db_session(test_engine) -> Generator[Session, None, None]:
    """
    Create a fresh database session for each test.
    Tables are created and dropped for complete isolation.
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)

    # Create session
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
async def async_db_session(test_async_engine) -> AsyncGenerator[AsyncSession, None]:
    """
    Create a fresh async database session for each test.
    """
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        test_async_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        yield session

    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def client(async_db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Create test HTTP client with database dependency override.
    """
    async def override_get_db():
        yield async_db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user_data() -> dict:
    """Standard test user data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "display_name": "Test User"
    }


@pytest.fixture(scope="function")
def test_admin_data() -> dict:
    """Standard test admin data."""
    return {
        "username": "testadmin",
        "email": "admin@example.com",
        "password": "adminpassword123",
        "display_name": "Test Admin",
        "is_admin": True,
        "is_approved": True
    }


@pytest.fixture(scope="function")
def create_test_user(db_session: Session):
    """Factory fixture to create test users."""
    def _create_user(
        username: str = "testuser",
        email: str = "test@example.com",
        password: str = "testpassword123",
        is_admin: bool = False,
        is_approved: bool = True
    ) -> User:
        user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            display_name=username.title(),
            is_admin=is_admin,
            is_approved=is_approved
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user


# ============================================================================
# Safety Check: Ensure we're not using production database
# ============================================================================

def pytest_configure(config):
    """
    Pytest hook to verify test environment before running any tests.
    """
    # Check environment variables
    assert os.environ.get("TESTING") == "true", \
        "TESTING environment variable must be 'true'"

    assert os.environ.get("POSTGRES_PORT") == "5434", \
        "Tests must use port 5434 (test database), not 5433 (production)"

    assert os.environ.get("POSTGRES_DB") == "wsoptv_test", \
        "Tests must use wsoptv_test database, not wsoptv"

    print("\n" + "="*60)
    print("TEST ENVIRONMENT VERIFIED")
    print(f"  Database: {os.environ.get('POSTGRES_HOST')}:{os.environ.get('POSTGRES_PORT')}")
    print(f"  DB Name:  {os.environ.get('POSTGRES_DB')}")
    print(f"  Redis:    {os.environ.get('REDIS_HOST')}:{os.environ.get('REDIS_PORT')}")
    print("="*60 + "\n")
