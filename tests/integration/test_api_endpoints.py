"""Integration tests for API endpoints."""

import pytest
from httpx import AsyncClient


class TestStatusEndpoint:
    """Test /status endpoint."""

    @pytest.mark.asyncio
    async def test_status_endpoint(self, async_client: AsyncClient) -> None:
        """Test that status endpoint returns ok."""
        response = await async_client.get("/status")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestAuthenticationEndpoint:
    """Test authentication on protected endpoints."""

    @pytest.mark.asyncio
    async def test_tasks_without_auth(self, async_client: AsyncClient) -> None:
        """Test that tasks endpoint requires authentication."""
        response = await async_client.get("/tasks")
        assert response.status_code == 401
        assert "Invalid or missing API key" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_tasks_with_invalid_auth(
        self, async_client: AsyncClient, invalid_auth_headers: dict[str, str]
    ) -> None:
        """Test that tasks endpoint rejects invalid API key."""
        response = await async_client.get("/tasks", headers=invalid_auth_headers)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_report_without_auth(self, async_client: AsyncClient) -> None:
        """Test that report endpoint requires authentication."""
        response = await async_client.get("/report")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_log_task_without_auth(self, async_client: AsyncClient) -> None:
        """Test that log_task endpoint requires authentication."""
        response = await async_client.post(
            "/log_task", json={"title": "Test task", "hours_spent": 2.0}
        )
        assert response.status_code == 401


class TestTasksEndpoint:
    """Test /tasks endpoint."""

    @pytest.mark.asyncio
    async def test_get_all_tasks(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test getting all tasks with authentication."""
        response = await async_client.get("/tasks", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert len(data["items"]) == 3
        assert data["total"] == 3

    @pytest.mark.asyncio
    async def test_get_tasks_with_pagination(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test pagination on tasks endpoint."""
        response = await async_client.get(
            "/tasks?page=1&page_size=2", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["total"] == 3
        assert data["page"] == 1
        assert data["page_size"] == 2
        assert data["total_pages"] == 2

    @pytest.mark.asyncio
    async def test_get_tasks_with_status_filter(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test filtering tasks by status."""
        response = await async_client.get(
            "/tasks?status=complete", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["status"] == "complete"

    @pytest.mark.asyncio
    async def test_get_tasks_invalid_page(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test that invalid page number is rejected."""
        response = await async_client.get("/tasks?page=0", headers=auth_headers)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_tasks_page_size_too_large(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test that page_size over limit is rejected."""
        response = await async_client.get("/tasks?page_size=101", headers=auth_headers)
        assert response.status_code == 422


class TestReportEndpoint:
    """Test /report endpoint."""

    @pytest.mark.asyncio
    async def test_get_report(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test getting productivity report."""
        response = await async_client.get("/report", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "total_tasks" in data
        assert "completed_tasks" in data
        assert "total_hours_spent" in data
        assert "completion_rate" in data
        assert data["total_tasks"] == 3
        assert data["completed_tasks"] == 1

    @pytest.mark.asyncio
    async def test_report_calculations(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test that report calculations are correct."""
        response = await async_client.get("/report", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_hours_spent"] == 23.5
        assert data["completion_rate"] == 0.33


class TestLogTaskEndpoint:
    """Test /log_task endpoint."""

    @pytest.mark.asyncio
    async def test_create_task(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test creating a new task."""
        task_data = {
            "title": "New test task",
            "status": "in_progress",
            "hours_spent": 5.0,
        }
        response = await async_client.post(
            "/log_task", json=task_data, headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Task logged successfully"
        assert "task_id" in data
        assert data["task_id"] == 4  # Should be next ID

    @pytest.mark.asyncio
    async def test_create_task_with_defaults(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test creating a task with default values."""
        task_data = {"title": "Simple task"}
        response = await async_client.post(
            "/log_task", json=task_data, headers=auth_headers
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_create_task_invalid_title(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test that empty title is rejected."""
        task_data = {"title": "", "hours_spent": 2.0}
        response = await async_client.post(
            "/log_task", json=task_data, headers=auth_headers
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_task_negative_hours(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test that negative hours are rejected."""
        task_data = {"title": "Valid task", "hours_spent": -5.0}
        response = await async_client.post(
            "/log_task", json=task_data, headers=auth_headers
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_task_persists_after_creation(
        self, async_client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Test that created task is retrievable."""
        # Create a task
        task_data = {"title": "Persistent task", "hours_spent": 3.0}
        create_response = await async_client.post(
            "/log_task", json=task_data, headers=auth_headers
        )
        assert create_response.status_code == 200

        # Verify it appears in the list
        list_response = await async_client.get("/tasks", headers=auth_headers)
        assert list_response.status_code == 200
        data = list_response.json()
        assert data["total"] == 4
        task_titles = [task["title"] for task in data["items"]]
        assert "Persistent task" in task_titles
