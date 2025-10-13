import asyncio

from utils.device_credentials import DeviceCredentials
from utils.process_device import process_device


class OneShotRunner:
    def __init__(self):
        self.active_tasks: set[asyncio.Task] = set()

    async def add_task_queue(self, credentials_queue):
        self.active_tasks.clear()

        while not credentials_queue.empty():
            device = await credentials_queue.get()
            task = asyncio.create_task(process_device(device))
            self.active_tasks.add(task)
            credentials_queue.task_done()

        await asyncio.gather(*self.active_tasks, return_exceptions=True)
        self.active_tasks.clear()

    async def stop_all_tasks(self):
        """Принудительная остановка всех задач"""
        for task in self.active_tasks:
            task.cancel()

        if self.active_tasks:
            await asyncio.gather(*self.active_tasks, return_exceptions=True)
        self.active_tasks.clear()


class PeriodicRunner:
    POLL_TIMEOUT = 10

    def __init__(self):
        self.tasks: set[asyncio.Task] = set()
        self.stop_events: dict[DeviceCredentials, asyncio.Event] = {}

    async def add_task_queue(self, credentials_queue):
        """Добавляет периодические задачи для каждого устройства"""
        while not credentials_queue.empty():
            device = await credentials_queue.get()
            stop_event = asyncio.Event()
            self.stop_events[device] = stop_event

            # Создаем периодическую задачу
            task = asyncio.create_task(self.periodic_device_worker(device, stop_event))
            self.tasks.add(task)
            credentials_queue.task_done()

    async def periodic_device_worker(self, device: DeviceCredentials, stop_event: asyncio.Event):
        """Периодически выполняет задачу для устройства"""
        while not stop_event.is_set():
            try:
                await process_device(device)
                await asyncio.sleep(self.POLL_TIMEOUT)  # Пауза POLL_TIMEOUT секунд между запусками
            except Exception as e:
                logger.error(f"Периодическая задача {device.ip}: {e}")
                await asyncio.sleep(self.POLL_TIMEOUT)  # Пауза при ошибке

    async def stop_all_tasks(self):
        """Останавливает все периодические задачи"""
        # Сигналим остановку
        for stop_event in self.stop_events.values():
            stop_event.set()

        # Ждем завершения задач
        if self.tasks:
            await asyncio.gather(*self.tasks, return_exceptions=True)

        # Очищаем
        self.tasks.clear()
        self.stop_events.clear()

    async def restart_with_new_queue(self, credentials_queue):
        """Останавливает старые задачи и запускает новые"""
        await self.stop_all_tasks()
        await self.add_task_queue(credentials_queue)

