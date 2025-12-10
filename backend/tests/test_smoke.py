"""
WSOPTV Smoke Tests

Critical path tests that must pass before any deployment.
These tests verify the core functionality of the system.

Run with: pytest tests/test_smoke.py -v
"""

import pytest
from httpx import AsyncClient


class TestSmokeAuth:
    """Authentication smoke tests."""

    @pytest.mark.asyncio
    async def test_login_endpoint_exists(self, client: AsyncClient):
        """[AUTH] Login endpoint should exist and accept POST."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"username": "invalid", "password": "invalid"}
        )
        # Should return 401 (unauthorized), not 404 (not found)
        assert response.status_code in [401, 422], \
            f"Login endpoint should exist, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_register_endpoint_exists(self, client: AsyncClient):
        """[AUTH] Register endpoint should exist and accept POST."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "username": "testuser",
                "password": "testpass123",
                "passwordConfirm": "testpass123"
            }
        )
        # Should return 201 (created) or 409 (conflict), not 404 (not found)
        assert response.status_code in [201, 409, 422], \
            f"Register endpoint should exist, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_me_endpoint_requires_auth(self, client: AsyncClient):
        """[AUTH] Me endpoint should require authentication."""
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401, \
            f"Me endpoint should require auth, got {response.status_code}"


class TestSmokeCatalog:
    """Catalog smoke tests."""

    @pytest.mark.asyncio
    async def test_catalogs_endpoint_exists(self, client: AsyncClient):
        """[CATALOG] Catalogs endpoint should exist and return list."""
        response = await client.get("/api/v1/catalogs")
        assert response.status_code == 200, \
            f"Catalogs endpoint should return 200, got {response.status_code}"

    @pytest.mark.asyncio
    async def test_catalogs_returns_items_array(self, client: AsyncClient):
        """[CATALOG] Catalogs should return items array."""
        response = await client.get("/api/v1/catalogs")
        data = response.json()

        assert "items" in data, "Response should contain 'items' key"
        assert isinstance(data["items"], list), "'items' should be a list"
        assert "total" in data, "Response should contain 'total' key"


class TestSmokeContent:
    """Content smoke tests."""

    @pytest.mark.asyncio
    async def test_contents_endpoint_exists(self, client: AsyncClient):
        """[CONTENT] Contents endpoint should exist."""
        response = await client.get("/api/v1/contents")
        # Should return 200 or 404 (empty), not 500
        assert response.status_code in [200, 404], \
            f"Contents endpoint should work, got {response.status_code}"


class TestSmokeSearch:
    """Search smoke tests."""

    @pytest.mark.asyncio
    async def test_search_endpoint_exists(self, client: AsyncClient):
        """[SEARCH] Search endpoint should exist and accept query."""
        response = await client.get("/api/v1/search", params={"q": "test"})
        # Should return 200 or empty results, not 500
        assert response.status_code in [200, 422], \
            f"Search endpoint should work, got {response.status_code}"


class TestSmokeHealth:
    """Health check smoke tests."""

    @pytest.mark.asyncio
    async def test_health_endpoint(self, client: AsyncClient):
        """[HEALTH] Health endpoint should return 200."""
        response = await client.get("/health")
        assert response.status_code == 200, \
            f"Health endpoint should return 200, got {response.status_code}"


# ============================================================================
# Smoke Test Runner
# ============================================================================

def run_smoke_tests():
    """
    Run smoke tests programmatically.
    Can be called from CI/CD pipeline or after domain work.
    """
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "-m", "pytest", __file__, "-v", "--tb=short"],
        capture_output=True,
        text=True
    )

    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return False
    return True


if __name__ == "__main__":
    success = run_smoke_tests()
    exit(0 if success else 1)
