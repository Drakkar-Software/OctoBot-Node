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
from typing import Optional, Any
import logging
from octobot_node.app.models import TaskStatus
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
            self.INSTANCE.stop()
            self.logger.info("Scheduler stopped")
        else:
            self.logger.warning("Scheduler not initialized")

    def get_periodic_tasks(self) -> list[dict]:
        return [{
                "id": task.id,
                "name": task.name,
                "description": f"Periodic task: {task.name} (runs every minute)",
                "status": TaskStatus.PERIODIC,
                "retries": task.retries,
                "expires_at": task.expires,
                "scheduled_at": None,
                "started_at": None,
                "completed_at": None,
            } for task in self.INSTANCE._registry.periodic_tasks]

    def get_pending_tasks(self) -> list[dict]:
        tasks: list[dict] = []
        pending_tasks = self.INSTANCE.pending()
        for task in pending_tasks or []:
            try:
                tasks.append({
                    "id": task.id,
                    "name": task.name,
                    "description": f"Pending task: {task.name}",
                    "status": TaskStatus.PENDING,
                    "scheduled_at": "",# task_metadata.get("scheduled_at"),
                    "started_at": None,
                    "completed_at": None,
                })
            except Exception as e:
                self.logger.warning("Failed to process pending task %s: %s", task.id, e)
        return tasks

    def get_scheduled_tasks(self) -> list[dict]:
        tasks: list[dict] = []
        scheduled_tasks = self.INSTANCE.scheduled()
        for task in scheduled_tasks or []:
            try:
                tasks.append({
                    "id": task.id,
                    "name": task.name,
                    "description": f"Scheduled task: {task.name}",
                    "status": TaskStatus.SCHEDULED,
                    "scheduled_at": "",# scheduled_at,
                    "started_at": "",# task_metadata.get("started_at"),
                    "completed_at": None,
                })
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

    def save_data(self, key: str, value: str) -> None:
        self.INSTANCE.storage.put_data(key, value)

    def get_data(self, key: str) -> str:
        return self.INSTANCE.storage.peek_data(key)
