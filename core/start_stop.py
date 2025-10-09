import logging
import os
import asyncio
from core.poller import AsyncPollManager
from core.poller_config import DevicesCredentialsParser
from core.extracted_config_saver import ExtractedConfigsSaver
from core.polling_report import StatusReport


class AdvancedNetworkMonitor:
    """Основной класс мониторинга, координирующий работу всех компонентов"""

    def __init__(self, config_path: str = None, poll_interval: int = 60,
                 config_check_interval: int = 30, simultaneous_tasks: int = 10):

        self.logger = logging.getLogger(f"{__name__}.AdvancedNetworkMonitor")
        self.logger.info("AdvancedNetworkMonitor инициализирован")

        # Определяем путь к конфигурационному файлу
        if config_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            self.config_path = os.path.join(script_dir, '..', 'credentials', 'credentials.yaml')
        else:
            self.config_path = config_path

        self.poll_interval = poll_interval
        self.config_check_interval = config_check_interval
        self.is_running = True

        # Инициализация компонентов
        self._initialize_components(simultaneous_tasks)

        self.logger.warning(f"Конфигурационный файл: {self.config_path}")

    def _initialize_components(self, simultaneous_tasks: int = 10):
        """Инициализация всех компонентов системы"""
        try:
            # 1. Инициализация менеджера конфигурации
            self.config_manager = DevicesCredentialsParser(self.config_path)
            self.logger.debug("ConfigManager инициализирован")

            # 2. Инициализация сохранения конфигураций
            self.config_saver = ExtractedConfigsSaver()
            self.logger.debug("ConfigSaver инициализирован")

            # 3. Инициализация трекера статусов
            self.status_tracker = StatusReport()
            self.logger.debug("StatusTracker инициализирован")

            # 4. Инициализация асинхронного опросчика
            self.device_poller = AsyncPollManager(
                self.config_saver,
                self.status_tracker,
                simultaneous_tasks
            )
            self.logger.debug("DevicePoller инициализирован")

        except ImportError as e:
            self.logger.exception(f"Ошибка импорта компонента: {e}")
            raise
        except Exception as e:
            self.logger.exception(f"Ошибка инициализации компонентов: {e}")
            raise

    async def start_monitoring(self):
        self.logger.debug("Запуск расширенного монитора сети")

        # Проверяем существование файла конфигурации
        if not os.path.exists(self.config_path):
            self.logger.error(f"Ошибка: Файл конфигурации не найден: {self.config_path}")
            return

        # Запускаем параллельные задачи
        await self.device_polling_loop()

    async def device_polling_loop(self):
        """Отдельный цикл для опроса устройств, опрашивает и далее ждет таймаут"""
        while self.is_running:
            try:
                await self.device_poller.poll_all_devices(self.config_manager.load_polling_network_device_credentials())
                self.status_tracker.print_status_report()
                self.logger.debug(f"Следующий опрос через {self.poll_interval} сек...")
                await asyncio.sleep(self.poll_interval)

            except Exception as e:
                self.logger.exception(f"Ошибка в цикле опроса: {e}")
                await asyncio.sleep(60)

    def stop(self):
        """Остановка монитора"""
        self.is_running = False
