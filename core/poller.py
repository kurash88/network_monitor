import logging
import asyncssh
import asyncio
from typing import List, Dict
from core.device import DeviceCredentials
from core.extract_commands import ExtractConfigFromDeviceCommands
from core.extracted_config_saver import ExtractedConfigsSaver
from core.polling_report import StatusReport


class NetworkDevicePoller:
    """Класс для сбора конфигурации с устройств"""

    logger = logging.getLogger("NetworkDevicePoller")

    @staticmethod
    async def poll_single_device(device: DeviceCredentials) -> Dict:
        """Вместо finaly использовал контекстный менеджер"""
        try:
            NetworkDevicePoller.logger.debug(f"Starting debug for {device.dev_type} ( {device.ip} )")

            async with asyncssh.connect(
                    host=device.ip,
                    username=device.username,
                    password=device.password,
                    known_hosts=None,
                    connect_timeout=30
            ) as conn:

                NetworkDevicePoller.logger.debug(f"Connected: {conn}")

                command = ExtractConfigFromDeviceCommands.get_extract_command(device.dev_type)
                NetworkDevicePoller.logger.debug(f"Command: {command}")

                result = await conn.run(command, timeout=30)
                NetworkDevicePoller.logger.debug(f"Result received, length: {len(result.stdout)}")

                return {
                    'host': device.ip,
                    'config': result.stdout,
                    'success': True
                }

        except Exception as e:
            NetworkDevicePoller.logger.exception(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'host': device.ip,
                'config': '',
                'success': False,
                'error': str(e)
            }


class AsyncPollManager:
    """Класс для параллельного опроса устройств"""

    def __init__(self,
                 config_saver: ExtractedConfigsSaver,
                 status_tracker: StatusReport, simultaneous_tasks: int = 10):
        self.config_saver = config_saver
        self.status_tracker = status_tracker
        self.simultaneous_tasks = simultaneous_tasks

        self.semaphore = asyncio.Semaphore(self.simultaneous_tasks)

        self.logger = logging.getLogger(f"{__name__}.AsyncPollManager")
        self.logger.info("AsyncPollManager инициализирован")

    async def _bounded_poll(self, device):
        async with self.semaphore:
            # return await self.config_collector.poll_single_device(device)
            return await NetworkDevicePoller.poll_single_device(device)

    async def poll_all_devices(self, devices: List[DeviceCredentials]):
        """Параллельный опрос всех устройств"""
        if not devices:
            self.logger.warning("Нет устройств для опроса")
            return

        self.logger.debug(f"\nНачинаем цикл опроса {len(devices)} устройств...")

        tasks = [self._bounded_poll(device) for device in devices]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for i, result in enumerate(results):
            device = devices[i]
            host = device.ip

            self.status_tracker.update_status(host, result)

            # Сохраняем конфигурацию если опрос успешен
            if isinstance(result, dict) and result.get('success'):
                await self.config_saver.save_config_if_changed(host, result['config'])
