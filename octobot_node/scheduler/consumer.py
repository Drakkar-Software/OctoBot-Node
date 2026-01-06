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
import threading

import logging
from octobot_node.app.core.config import settings

from octobot_node.scheduler.scheduler import Scheduler
from huey.constants import WORKER_THREAD
from huey.consumer import Consumer
from huey.consumer_options import ConsumerConfig
from huey.consumer_options import OptionParserHandler

class SchedulerConsumer:
    def __init__(self, scheduler: Scheduler):
        self.scheduler: Scheduler = scheduler
        self.consumer = None
        self.thread = None
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
    
    def start(self):
        with self.lock:
            if self.thread is None or not self.thread.is_alive():
                self.start_thread()
                self.logger.info("Scheduler consumer thread started automatically on import")
    
    def _run(self):
        parser_handler = OptionParserHandler()
        parser = parser_handler.get_option_parser()
        options, args = parser.parse_args()

        options = {k: v for k, v in options.__dict__.items()
                if v is not None}
        config = ConsumerConfig(**options)
        config.validate()

        logger = logging.getLogger('huey')
        config.setup_logger(logger)
        logging.info("starting consumer")
        config.values['worker_type'] = WORKER_THREAD
        consumer = self.scheduler.INSTANCE.create_consumer(**config.values)
        try:
            consumer.run()
        except ValueError as e:
            # Ignore `ValueError: signal only works in main thread of the main interpreter``
            self.logger.debug(f"ValueError ignored when starting consumer: {e}")

    def start_thread(self) -> None:
        if settings.SCHEDULER_NODE_TYPE == "master":
            self.logger.info("Node is configured as master - skipping consumer startup")
            return
        self.logger.info("Starting scheduler consumer")
        config_values = {
            "worker_type": WORKER_THREAD,
            "workers": settings.SCHEDULER_WORKERS,
        }
        self.consumer = self.scheduler.INSTANCE.create_consumer(**config_values)
        self.logger.info(
            "Scheduler consumer started with %d workers (worker_type=thread)",
            settings.SCHEDULER_WORKERS
        )
        self.thread = threading.Thread(
            target=self._run,
            args=(),
            name="scheduler-consumer",
            daemon=True,
        )
        self.thread.start()
        self.logger.info("Scheduler consumer running in thread")

    def is_started(self) -> bool:
        with self.lock:
            return self.thread is not None

    def is_running(self) -> bool:
        with self.lock:
            return self.thread is not None and self.thread.is_alive()

    def stop(self) -> None:
        with self.lock:
            if not self.consumer:
                return

            self.consumer.stop(graceful=True)
            if self.thread:
                self.thread.join(timeout=5)

            self.logger.info("Scheduler consumer stopped")
            self.consumer = None
            self.thread = None
