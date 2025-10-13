import asyncio
import logging

from utils.config import yaml_to_credentials, DeviceCredentials, get_config_contents
from utils.runners import OneShotRunner, PeriodicRunner

logger = logging.getLogger("read_config_file")


class TaskManager:
    def __init__(self, path: str, one_shot_runner: OneShotRunner, periodic_runner: PeriodicRunner):
        self.path = path
        self.one_shot_runner = one_shot_runner
        self.periodic_runner = periodic_runner

    async def make_queue_by_watch_status(self, for_periodic: bool = False) -> asyncio.Queue[DeviceCredentials]:
        file_data = await get_config_contents(self.path)
        credentials_unfiltered = yaml_to_credentials(file_data)
        if for_periodic:
            credentials = [cred for cred in credentials_unfiltered if cred.watch]
        else:
            credentials = [cred for cred in credentials_unfiltered if not cred.watch]

        queue = asyncio.Queue()
        for device in credentials:
            await queue.put(device)
        return queue

    async def add_task_queues_to_runners(self):
        oneshot_queue = await self.make_queue_by_watch_status(False)
        periodic_queue = await self.make_queue_by_watch_status(True)

        # Запускаем параллельно
        await asyncio.gather(
            self.one_shot_runner.add_task_queue(oneshot_queue),
            self.periodic_runner.restart_with_new_queue(periodic_queue)
        )
