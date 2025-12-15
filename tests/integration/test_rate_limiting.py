"""Integration tests for rate limiting."""

import pytest
from httpx import AsyncClient
import asyncio


class TestRateLimiting:
    """Test rate limiting on endpoints."""

    @pytest.mark.asyncio
    async def test_tasks_rate_limit(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test that tasks endpoint enforces rate limiting (10/minute)."""
        # Make 10 requests (should all succeed)
        for _ in range(10):
            response = await async_client.get("/tasks", headers=auth_headers)
            assert response.status_code == 200

        # The 11th request should be rate limited
        response = await async_client.get("/tasks", headers=auth_headers)
        assert response.status_code == 429  # Too Many Requests

    @pytest.mark.asyncio
    async def test_report_rate_limit(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test that report endpoint enforces rate limiting (5/minute)."""
        # Make 5 requests (should all succeed)
        for _ in range(5):
            response = await async_client.get("/report", headers=auth_headers)
            assert response.status_code == 200

        # The 6th request should be rate limited
        response = await async_client.get("/report", headers=auth_headers)
        assert response.status_code == 429

    @pytest.mark.asyncio
    async def test_log_task_rate_limit(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test that log_task endpoint enforces rate limiting (20/minute)."""
        task_data = {"title": "Rate limit test task", "hours_spent": 1.0}

        # Make 20 requests (should all succeed)
        for i in range(20):
            response = await async_client.post(
                "/log_task", json=task_data, headers=auth_headers
            )
            assert response.status_code == 200

        # The 21st request should be rate limited
        response = await async_client.post(
            "/log_task", json=task_data, headers=auth_headers
        )
        assert response.status_code == 429
