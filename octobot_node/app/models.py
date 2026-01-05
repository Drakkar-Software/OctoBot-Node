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

import uuid
import datetime
from enum import Enum

from pydantic import EmailStr
from pydantic import BaseModel, Field


class UserBase(BaseModel):
    email: EmailStr = Field(max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class User(UserBase):
    id: uuid.UUID


class TaskStatus(str, Enum):
    """Task status enumeration."""

    PENDING = "pending"
    SCHEDULED = "scheduled"
    PERIODIC = "periodic"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Task(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    status: TaskStatus
    retries: int = 0
    expires_at: datetime.datetime | None = None
    scheduled_at: datetime.datetime | None = None
    started_at: datetime.datetime | None = None
    completed_at: datetime.datetime | None = None

class TaskCreate(BaseModel):
    name: str
    description: str

class TaskUpdate(BaseModel):
    name: str
    description: str

class TaskDelete(Task):
    id: uuid.UUID


class Node(BaseModel):
    node_type: str
    backend_type: str
    workers: int | None
    status: str
    redis_url: str | None = None
    sqlite_file: str | None = None
