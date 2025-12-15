"""Shared pytest fixtures for testing."""

import pytest
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from fastapi.testclient import TestClient
from app.main import app, MOCK_TASKS, limiter
from app.models import DeveloperTask, TaskStatus


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Returns valid authentication headers."""
    return {"x-api-key": "dev-api-key-12345"}


@pytest.fixture
def invalid_auth_headers() -> dict[str, str]:
    """Returns invalid authentication headers."""
    return {"x-api-key": "invalid-key"}


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Provides an async HTTP client for testing."""
    transport = ASGITransport(app=app)  # type: ignore
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="function")
def sync_client() -> TestClient:
    """Provides a synchronous test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_mock_data() -> None:
    """Reset mock data and rate limiter before each test."""
    # Reset mock tasks
    MOCK_TASKS.clear()
    MOCK_TASKS.update(
        {
            1: DeveloperTask(
                task_id=1,
                title="Refactor legacy service",
                status=TaskStatus.COMPLETE,
                hours_spent=8.5,
            ),
            2: DeveloperTask(
                task_id=2,
                title="Implement new user auth flow",
                status=TaskStatus.IN_PROGRESS,
                hours_spent=15.0,
            ),
            3: DeveloperTask(
                task_id=3,
                title="Write unit tests for checkout",
                status=TaskStatus.PENDING,
                hours_spent=0.0,
            ),
        }
    )

    # Reset rate limiter
    limiter.reset()


# Configure pytest-asyncio
pytest_plugins = ("pytest_asyncio",)
