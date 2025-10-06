import asyncio
from typing import List, Dict
from devices.collector import ConfigCollector
from config.saver import ConfigSaver
from status.tracker import StatusTracker


class DevicePoller:
    """Класс для параллельного опроса устройств"""

    def __init__(self, config_collector: ConfigCollector, config_saver: ConfigSaver,
                 status_tracker: StatusTracker, simultaneous_tasks: int = 10):
        self.config_collector = config_collector
        self.config_saver = config_saver
        self.status_tracker = status_tracker
        self.simultaneous_tasks = simultaneous_tasks

    async def poll_all_devices(self, devices: List[dict]):
        """Параллельный опрос всех устройств"""
        if not devices:
            print("Нет устройств для опроса")
            return

        print(f"\nНачинаем цикл опроса {len(devices)} устройств...")

        semaphore = asyncio.Semaphore(self.simultaneous_tasks)

        async def bounded_poll(device):
            async with semaphore:
                # return await self.config_collector.poll_single_device(device)
                return await self.config_collector.debug_poll_single_device(device)

        tasks = [bounded_poll(device) for device in devices]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            device = devices[i]
            host = device['credentials']['host']

            self.status_tracker.update_status(host, result)

            # Сохраняем конфигурацию если опрос успешен
            if isinstance(result, dict) and result.get('success'):
                await self.config_saver.save_config_if_changed(host, result['config'])
