#  This file is part of OctoBot Node (https://github.com/Drakkar-Software/OctoBot-Node)
#  Copyright (c) 2025 Drakkar-Software, All rights reserved.
#
#  OctoBot is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  OctoBot is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public
#  License along with OctoBot. If not, see <https://www.gnu.org/licenses/>.

from typing import Any, List
import uuid
from fastapi import APIRouter

from octobot_node.app.models import Task, TaskCreate, TaskUpdate, TaskDelete, TaskStatus
from octobot_node.scheduler.api import get_all_tasks, get_task_metrics
from octobot_node.scheduler.tasks import ping_task

router = APIRouter(tags=["tasks"])

@router.post("/", response_model=Task)
def create_task(task: TaskCreate) -> Any:
    # TODO WIP
    return Task(
        id=uuid.uuid4(),
        name=task.name,
        description=task.description,
        status=TaskStatus.PENDING,
        scheduled_at=None,
        started_at=None,
        completed_at=None,
    )

@router.get("/metrics")
def get_metrics() -> Any:
    return get_task_metrics()

@router.get("/", response_model=List[Task])
def get_tasks(page: int = 1, limit: int = 100) -> Any:
    tasks_data = get_all_tasks()
    
    # Apply pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_tasks = tasks_data[start_idx:end_idx]
    
    return [Task(**task_data) for task_data in paginated_tasks]

@router.put("/", response_model=Task)
def update_task(taskId: uuid.UUID, task: TaskUpdate) -> Any:
    # TODO
    return task

@router.delete("/", response_model=TaskDelete)
def delete_task(taskId: uuid.UUID) -> Any:
    # TODO
    return taskId

@router.post("/ping", response_model=Task)
def trigger_ping() -> Any:
    # TODO remove (test only)
    result = ping_task.schedule(args=(), delay=2)
    
    return Task(
        id=uuid.uuid4(),
        name="ping",
        description=f"Manual ping trigger",
        status=TaskStatus.PENDING,
        scheduled_at=None,
        started_at=None,
        completed_at=None,
    )
