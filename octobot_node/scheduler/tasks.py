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
import json
from typing import Optional

from octobot_node.scheduler import SCHEDULER
from octobot_node.app.models import Task, TaskType

logger = logging.getLogger(__name__)



@SCHEDULER.INSTANCE.task()
def start_octobot(task: Task):
    # TODO
    return {"status": "done", "result": {}, "error": None}


@SCHEDULER.INSTANCE.task()
def execute_octobot(task: Task):
    decrypted_content = decrypt_content(task.content)

    if task.type == TaskType.EXECUTE_ACTIONS.value:
        # TODO start_octobot with actions
        print(f"Executing actions with content: {decrypted_content}...")
        return {"status": "done", "result": {}, "error": None}
    else:
        raise ValueError(f"Invalid task type: {type}")


@SCHEDULER.INSTANCE.task()
def stop_octobot(task: Task):
    # TODO
    return {"status": "done", "result": {}, "error": None}

def decrypt_content(content: str) -> str:
    # TODO
    return content

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
