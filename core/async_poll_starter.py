import asyncio
from typing import List, Dict
from devices.network_device_poller import NetworkDevicePoller
from config.network_devices_extracted_config_saver import NetworkDevicesExtractedConfigsSaver
from status.network_device_status_tracker import NetworkDeviceStatusTracker


class AsyncPollStarter:
    """Класс для параллельного опроса устройств"""

    def __init__(self, config_collector: NetworkDevicePoller, config_saver: NetworkDevicesExtractedConfigsSaver,
                 status_tracker: NetworkDeviceStatusTracker, simultaneous_tasks: int = 10):
        self.config_collector = config_collector
        self.config_saver = config_saver
        self.status_tracker = status_tracker
        self.simultaneous_tasks = simultaneous_tasks

        self.semaphore = asyncio.Semaphore(self.simultaneous_tasks)

    async def _bounded_poll(self, device):
        async with self.semaphore:
            # return await self.config_collector.poll_single_device(device)
            return await self.config_collector.debug_poll_single_device(device)

    async def poll_all_devices(self, devices: List[dict]):
        """Параллельный опрос всех устройств"""
        if not devices:
            print("Нет устройств для опроса")
            return

        print(f"\nНачинаем цикл опроса {len(devices)} устройств...")

        tasks = [self._bounded_poll(device) for device in devices]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            device = devices[i]
            host = device['credentials']['host']

            self.status_tracker.update_status(host, result)

            # Сохраняем конфигурацию если опрос успешен
            if isinstance(result, dict) and result.get('success'):
                await self.config_saver.save_config_if_changed(host, result['config'])
