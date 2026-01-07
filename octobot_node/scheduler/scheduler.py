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

from huey import Huey, RedisHuey, SqliteHuey
from huey.registry import Message
from typing import Optional, Any
import logging
from octobot_node.app.models import Task, TaskType, TaskStatus
from octobot_node.app.core.config import settings

class Scheduler:
    INSTANCE: Optional[Huey] = None

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    def create(self):
        if settings.SCHEDULER_REDIS_URL:
            self.logger.info(
                "Initializing scheduler with Redis backend at %s", settings.SCHEDULER_REDIS_URL
            )
            self.INSTANCE = RedisHuey("octobot-node", url=str(settings.SCHEDULER_REDIS_URL))
        else:
            self.logger.info(
                "Initializing scheduler with sqlite backend at %s", settings.SCHEDULER_SQLITE_FILE
            )
            self.INSTANCE = SqliteHuey("octobot-node", filename=settings.SCHEDULER_SQLITE_FILE)

    def stop(self) -> None:
        if self.INSTANCE:
            # TODO self.INSTANCE.stop()
            self.logger.info("Scheduler stopped")
        else:
            self.logger.warning("Scheduler not initialized")

    def get_periodic_tasks(self) -> list[dict]:
        tasks: list[dict] = []
        periodic_tasks = self.INSTANCE._registry.periodic_tasks
        for task in periodic_tasks or []:
            try:
                tasks.append(self._parse_task(task, "Periodic task: {task.name}", TaskStatus.PERIODIC))
            except Exception as e:
                self.logger.warning("Failed to process periodic task %s: %s", task.id, e)
        return tasks

    def get_pending_tasks(self) -> list[dict]:
        tasks: list[dict] = []
        pending_tasks = self.INSTANCE.pending()
        for task in pending_tasks or []:
            try:
                tasks.append(self._parse_task(task, "Pending task: {task.name}", TaskStatus.PENDING))
            except Exception as e:
                self.logger.warning("Failed to process pending task %s: %s", task.id, e)
        return tasks

    def get_scheduled_tasks(self) -> list[dict]:
        tasks: list[dict] = []
        scheduled_tasks = self.INSTANCE.scheduled()
        for task in scheduled_tasks or []:
            try:
                tasks.append(self._parse_task(task, "Scheduled task: {task.name}", TaskStatus.SCHEDULED))
            except Exception as e:
                self.logger.warning("Failed to process scheduled task %s: %s", task.id, e)
        return tasks

    def get_results(self) -> list[dict]:
        tasks: list[dict] = []
        result_keys = self.INSTANCE.all_results()
        for result_key in result_keys:
            try:
                tasks.append({
                    "id": result_key,
                    "name": result_key,
                    "description": f"Task completed",
                    "status": TaskStatus.COMPLETED,
                    "scheduled_at": None,
                    "started_at": None,
                    "completed_at": None,
                })
            except Exception as e:
                self.logger.debug("Failed to process result key %s: %s", result_key, e)
        return tasks


    def _parse_task(self, message: Message, status: TaskStatus, description: Optional[str] = None) -> Task:
        task_kwargs = message.kwargs
        task_actions = task_kwargs.get("actions")
        task_type = task_kwargs.get("type")

        return Task(
            id=message.id,
            name=message.name,
            description=description,
            actions=task_actions,
            type=TaskType(task_type) if task_type else None,
            status=status,
            retries=message.retries,
            retry_delay=message.retry_delay,
            priority=message.priority,
            expires=message.expires,
            expires_resolved=message.expires_resolved,
            scheduled_at=message.eta,
            started_at=None,
            completed_at=None,
        )


    def save_data(self, key: str, value: str) -> None:
        self.INSTANCE.storage.put_data(key, value)

    def get_data(self, key: str) -> str:
        return self.INSTANCE.storage.peek_data(key)
