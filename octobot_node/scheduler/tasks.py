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

import logging

from octobot_node.scheduler.encryption import decrypt_task_content
from octobot_node.scheduler import SCHEDULER
from octobot_node.app.core.config import settings
from octobot_node.app.models import Task, TaskType
from octobot_node.app.enums import TaskResultKeys


logger = logging.getLogger(__name__)



@SCHEDULER.INSTANCE.task()
def start_octobot(task: Task):
    # TODO
    return {
        TaskResultKeys.STATUS.value: "done", 
        TaskResultKeys.TASK.value: {"name": task.name}, 
        TaskResultKeys.RESULT.value: {}, 
        TaskResultKeys.ERROR.value: None
    }


@SCHEDULER.INSTANCE.task()
def execute_octobot(task: Task):
    if settings.TASKS_INPUTS_RSA_PRIVATE_KEY:
        try:
            decrypted_content = decrypt_task_content(task.content, task.metadata)
        except Exception as e:
            logger.error(f"Failed to decrypt content: {e}")
            return {
                TaskResultKeys.STATUS.value: "failed", 
                TaskResultKeys.TASK.value: {"name": task.name}, 
                TaskResultKeys.RESULT.value: {}, 
                TaskResultKeys.ERROR.value: str(e)
            }
    else:
        decrypted_content = task.content

    if task.type == TaskType.EXECUTE_ACTIONS.value:
        # TODO start_octobot with actions
        print(f"Executing actions with content: {decrypted_content}...")
        return {
            TaskResultKeys.STATUS.value: "done", 
            TaskResultKeys.TASK.value: {"name": task.name}, 
            TaskResultKeys.RESULT.value: {}, 
            TaskResultKeys.ERROR.value: None
        }
    else:
        raise ValueError(f"Invalid task type: {type}")


@SCHEDULER.INSTANCE.task()
def stop_octobot(task: Task):
    # TODO
    return {TaskResultKeys.STATUS.value: "done", TaskResultKeys.TASK.value: {"name": task.name}, TaskResultKeys.RESULT.value: {}, TaskResultKeys.ERROR.value: None}

def trigger_task(task: Task) -> bool:
    if task.type == TaskType.START_OCTOBOT.value:
        start_octobot.schedule(args=[task], delay=1)
        return True
    elif task.type == TaskType.STOP_OCTOBOT.value:
        stop_octobot.schedule(args=[task], delay=1)
        return True
    elif task.type == TaskType.EXECUTE_ACTIONS.value:
        execute_octobot.schedule(args=[task], delay=1)
        return True
    else:
        raise ValueError(f"Invalid task type: {task.type}")
