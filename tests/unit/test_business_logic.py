"""Unit tests for business logic functions."""

import pytest
from app.main import fetch_all_tasks, generate_productivity_report, MOCK_TASKS
from app.models import TaskStatus, DeveloperTask
from fastapi import HTTPException


class TestFetchAllTasks:
    """Test fetch_all_tasks function."""

    @pytest.mark.asyncio
    async def test_fetch_all_tasks_no_filter(self) -> None:
        """Test fetching all tasks without filters."""
        tasks, total = await fetch_all_tasks()
        assert len(tasks) == 3
        assert total == 3

    @pytest.mark.asyncio
    async def test_fetch_tasks_with_status_filter(self) -> None:
        """Test fetching tasks with status filter."""
        tasks, total = await fetch_all_tasks(status_filter=TaskStatus.COMPLETE)
        assert len(tasks) == 1
        assert total == 1
        assert tasks[0].status == TaskStatus.COMPLETE

    @pytest.mark.asyncio
    async def test_fetch_tasks_with_pagination(self) -> None:
        """Test fetching tasks with pagination."""
        tasks, total = await fetch_all_tasks(skip=1, limit=1)
        assert len(tasks) == 1
        assert total == 3

    @pytest.mark.asyncio
    async def test_fetch_tasks_pagination_beyond_range(self) -> None:
        """Test fetching tasks with pagination beyond available data."""
        tasks, total = await fetch_all_tasks(skip=10, limit=10)
        assert len(tasks) == 0
        assert total == 3

    @pytest.mark.asyncio
    async def test_fetch_tasks_combined_filter_and_pagination(self) -> None:
        """Test combining status filter and pagination."""
        MOCK_TASKS.update(
            {
                4: DeveloperTask(
                    task_id=4,
                    title="Task 4",
                    status=TaskStatus.COMPLETE,
                    hours_spent=2.0,
                ),
                5: DeveloperTask(
                    task_id=5,
                    title="Task 5",
                    status=TaskStatus.COMPLETE,
                    hours_spent=3.0,
                ),
            }
        )
        tasks, total = await fetch_all_tasks(
            status_filter=TaskStatus.COMPLETE, skip=1, limit=1
        )
        assert len(tasks) == 1
        assert total == 3  # Total complete tasks


class TestGenerateProductivityReport:
    """Test generate_productivity_report function."""

    @pytest.mark.asyncio
    async def test_generate_report_with_data(self) -> None:
        """Test generating report with existing tasks."""
        report = await generate_productivity_report()
        assert report.total_tasks == 3
        assert report.completed_tasks == 1
        assert report.total_hours_spent == 23.5
        assert report.completion_rate == 0.33

    @pytest.mark.asyncio
    async def test_generate_report_empty_database(self) -> None:
        """Test generating report with no tasks."""
        MOCK_TASKS.clear()
        report = await generate_productivity_report()
        assert report.total_tasks == 0
        assert report.completed_tasks == 0
        assert report.total_hours_spent == 0.0
        assert report.completion_rate == 0.0

    @pytest.mark.asyncio
    async def test_generate_report_all_complete(self) -> None:
        """Test generating report when all tasks are complete."""
        MOCK_TASKS.clear()
        MOCK_TASKS.update(
            {
                1: DeveloperTask(
                    task_id=1,
                    title="Task 1",
                    status=TaskStatus.COMPLETE,
                    hours_spent=5.0,
                ),
                2: DeveloperTask(
                    task_id=2,
                    title="Task 2",
                    status=TaskStatus.COMPLETE,
                    hours_spent=3.0,
                ),
            }
        )
        report = await generate_productivity_report()
        assert report.total_tasks == 2
        assert report.completed_tasks == 2
        assert report.total_hours_spent == 8.0
        assert report.completion_rate == 1.0
