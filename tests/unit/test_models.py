"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError
from app.models import (
    TaskStatus,
    DeveloperTask,
    ProductivityReport,
    TaskCreateRequest,
    PaginatedResponse,
    TaskResponse,
)


class TestTaskStatus:
    """Test TaskStatus enum."""

    def test_task_status_values(self) -> None:
        """Test that TaskStatus has the correct values."""
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.IN_PROGRESS == "in_progress"
        assert TaskStatus.COMPLETE == "complete"

    def test_task_status_from_string(self) -> None:
        """Test creating TaskStatus from string."""
        status = TaskStatus("pending")
        assert status == TaskStatus.PENDING


class TestDeveloperTask:
    """Test DeveloperTask model."""

    def test_create_task_with_defaults(self) -> None:
        """Test creating a task with default values."""
        task = DeveloperTask(task_id=1, title="Test task")
        assert task.task_id == 1
        assert task.title == "Test task"
        assert task.status == TaskStatus.PENDING
        assert task.hours_spent == 0.0

    def test_create_task_with_all_fields(self) -> None:
        """Test creating a task with all fields specified."""
        task = DeveloperTask(
            task_id=1,
            title="Test task",
            status=TaskStatus.COMPLETE,
            hours_spent=5.5,
        )
        assert task.task_id == 1
        assert task.title == "Test task"
        assert task.status == TaskStatus.COMPLETE
        assert task.hours_spent == 5.5


class TestTaskCreateRequest:
    """Test TaskCreateRequest model."""

    def test_valid_task_request(self) -> None:
        """Test creating a valid task request."""
        request = TaskCreateRequest(title="New task", hours_spent=3.0)
        assert request.title == "New task"
        assert request.status == TaskStatus.PENDING
        assert request.hours_spent == 3.0

    def test_title_too_short(self) -> None:
        """Test that empty title is rejected."""
        with pytest.raises(ValidationError):
            TaskCreateRequest(title="")

    def test_title_too_long(self) -> None:
        """Test that overly long title is rejected."""
        with pytest.raises(ValidationError):
            TaskCreateRequest(title="x" * 201)

    def test_negative_hours(self) -> None:
        """Test that negative hours are rejected."""
        with pytest.raises(ValidationError):
            TaskCreateRequest(title="Valid title", hours_spent=-1.0)


class TestProductivityReport:
    """Test ProductivityReport model."""

    def test_create_report(self) -> None:
        """Test creating a productivity report."""
        report = ProductivityReport(
            total_tasks=10,
            completed_tasks=7,
            total_hours_spent=45.5,
            completion_rate=0.7,
        )
        assert report.total_tasks == 10
        assert report.completed_tasks == 7
        assert report.total_hours_spent == 45.5
        assert report.completion_rate == 0.7


class TestPaginatedResponse:
    """Test PaginatedResponse model."""

    def test_create_paginated_response(self) -> None:
        """Test creating a paginated response."""
        tasks = [
            DeveloperTask(task_id=1, title="Task 1"),
            DeveloperTask(task_id=2, title="Task 2"),
        ]
        response = PaginatedResponse(
            items=tasks,
            total=10,
            page=1,
            page_size=2,
            total_pages=5,
        )
        assert len(response.items) == 2
        assert response.total == 10
        assert response.page == 1
        assert response.page_size == 2
        assert response.total_pages == 5


class TestTaskResponse:
    """Test TaskResponse model."""

    def test_create_task_response(self) -> None:
        """Test creating a task response."""
        response = TaskResponse(message="Success", task_id=42)
        assert response.message == "Success"
        assert response.task_id == 42
