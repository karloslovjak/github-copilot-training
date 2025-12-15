from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Available statuses for any task."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"


class DeveloperTask(BaseModel):
    """Model for a single task logged by a developer."""

    task_id: int
    title: str
    status: TaskStatus = TaskStatus.PENDING
    hours_spent: float = 0.0


class ProductivityReport(BaseModel):
    """The final calculated report."""

    total_tasks: int
    completed_tasks: int
    total_hours_spent: float
    completion_rate: float


class TaskCompletionMetrics(BaseModel):
    """Metrics related to task completion."""

    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    completion_rate: float  # Percentage of tasks completed


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""

    items: list[DeveloperTask]
    total: int
    page: int
    page_size: int
    total_pages: int


class TaskCreateRequest(BaseModel):
    """Request model for creating a new task."""

    title: str = Field(..., min_length=1, max_length=200)
    status: TaskStatus = TaskStatus.PENDING
    hours_spent: float = Field(default=0.0, ge=0.0)


class TaskResponse(BaseModel):
    """Response model for task creation."""

    message: str
    task_id: int
