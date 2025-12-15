from typing import Dict, Optional
import asyncio
from typing import List
from fastapi import FastAPI, HTTPException, Depends, Query, Header, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import math
from app.models import (
    TaskStatus,
    DeveloperTask,
    ProductivityReport,
    PaginatedResponse,
    TaskCreateRequest,
    TaskResponse,
)


# --- Rate Limiting Setup ---
limiter = Limiter(key_func=get_remote_address)


# --- Authentication ---
async def get_current_user(x_api_key: Optional[str] = Header(None)) -> str:
    """Simple API key authentication."""
    if not x_api_key or x_api_key != "dev-api-key-12345":
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return "authenticated_user"


# --- Mock Database / In-Memory Service Logic
MOCK_TASKS: Dict[int, DeveloperTask] = {
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


# Simulate asynchronous I/O with a slight delay
async def fetch_all_tasks(
    status_filter: Optional[TaskStatus] = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[List[DeveloperTask], int]:
    """Simulates fetching tasks asynchronously with filtering and pagination."""
    try:
        await asyncio.sleep(0.01)
        tasks = list(MOCK_TASKS.values())

        # Apply status filter if provided
        if status_filter:
            tasks = [task for task in tasks if task.status == status_filter]

        total = len(tasks)

        # Apply pagination
        tasks = tasks[skip : skip + limit]

        return tasks, total
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tasks: {str(e)}")


async def generate_productivity_report() -> ProductivityReport:
    """Calculates key metrics based on all tasks."""
    try:
        tasks, _ = await fetch_all_tasks()

        total_tasks = len(tasks)
        completed_tasks = sum(1 for task in tasks if task.status == TaskStatus.COMPLETE)

        total_hours_spent = sum(task.hours_spent for task in tasks)
        completion_rate = (
            round(completed_tasks / total_tasks, 2) if total_tasks > 0 else 0.0
        )

        return ProductivityReport(
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            total_hours_spent=round(total_hours_spent, 2),
            completion_rate=completion_rate,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating report: {str(e)}"
        )


# --- FastAPI Initialization and Routes ---
app = FastAPI(title="Productivity Reporting System")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore


@app.get("/status")
async def get_status() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/tasks", response_model=PaginatedResponse)
@limiter.limit("10/minute")
async def get_all_tasks(
    request: Request,
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    current_user: str = Depends(get_current_user),
) -> PaginatedResponse:
    """Returns a paginated list of tasks with optional status filtering."""
    skip = (page - 1) * page_size
    tasks, total = await fetch_all_tasks(
        status_filter=status, skip=skip, limit=page_size
    )

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedResponse(
        items=tasks,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@app.get("/report", response_model=ProductivityReport)
@limiter.limit("5/minute")
async def get_productivity_report(
    request: Request,
    current_user: str = Depends(get_current_user),
) -> ProductivityReport:
    """Returns the calculated productivity report."""
    return await generate_productivity_report()


@app.post("/log_task", response_model=TaskResponse)
@limiter.limit("20/minute")
async def log_task(
    request: Request,
    task_data: TaskCreateRequest,
    current_user: str = Depends(get_current_user),
) -> TaskResponse:
    """Creates a new task with validation."""
    try:
        new_id = max(MOCK_TASKS.keys()) + 1 if MOCK_TASKS else 1
        task = DeveloperTask(
            task_id=new_id,
            title=task_data.title,
            status=task_data.status,
            hours_spent=task_data.hours_spent,
        )
        MOCK_TASKS[new_id] = task

        return TaskResponse(message="Task logged successfully", task_id=task.task_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")
