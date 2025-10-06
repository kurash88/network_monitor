import os
import asyncio
from typing import List, Dict
from config.manager import ConfigManager
from devices.collector import ConfigCollector
from config.saver import ConfigSaver
from status.tracker import StatusTracker
from core.poller import DevicePoller


class AdvancedNetworkMonitor:
    """Основной класс мониторинга, координирующий работу всех компонентов"""

    def __init__(self, config_path: str = None, poll_interval: int = 60, 
                 config_check_interval: int = 30, simultaneous_tasks: int = 10):
        
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
        self.config_manager = ConfigManager(self.config_path)
        self.config_collector = ConfigCollector(self.config_manager)
        self.config_saver = ConfigSaver()
        self.status_tracker = StatusTracker()
        self.device_poller = DevicePoller(
            self.config_collector, 
            self.config_saver, 
            self.status_tracker,
            simultaneous_tasks
        )
        
        self.devices: List[dict] = []

        print(f"Конфигурационный файл: {self.config_path}")

    async def start_monitoring(self):
        """Запуск мониторинга с несколькими параллельными задачами"""
        print("Запуск расширенного монитора сети")

        # Проверяем существование файла конфигурации
        if not os.path.exists(self.config_path):
            print(f"Ошибка: Файл конфигурации не найден: {self.config_path}")
            return

        # Загружаем начальную конфигурацию
        self.devices = self.config_manager.load_config()

        # Запускаем параллельные задачи
        await asyncio.gather(
            self.config_monitor_loop(),
            self.device_polling_loop(),
            self.status_report_loop(),
            return_exceptions=True
        )

    async def config_monitor_loop(self):
        """Отдельный цикл для мониторинга изменений конфигурации"""
        while self.is_running:
            try:
                if not os.path.exists(self.config_path):
                    print(f"Файл конфигурации не найден: {self.config_path}")
                    await asyncio.sleep(self.config_check_interval)
                    continue

                if self.config_manager.config_modified():
                    print("Обновление конфигурации устройств...")
                    self.devices = self.config_manager.load_config()

                await asyncio.sleep(self.config_check_interval)

            except Exception as e:
                print(f"Ошибка в мониторинге конфигурации: {e}")
                await asyncio.sleep(30)

    async def device_polling_loop(self):
        """Отдельный цикл для опроса устройств"""
        while self.is_running:
            try:
                await self.device_poller.poll_all_devices(self.devices)
                print(f"Следующий опрос через {self.poll_interval} сек...")
                await asyncio.sleep(self.poll_interval)

            except Exception as e:
                print(f"Ошибка в цикле опроса: {e}")
                await asyncio.sleep(60)

    async def status_report_loop(self):
        """Цикл для периодического отчета о статусе"""
        report_interval = 600

        while self.is_running:
            try:
                await asyncio.sleep(report_interval)
                self.status_tracker.print_status_report()
            except Exception as e:
                print(f"Ошибка в цикле отчетов: {e}")

    def stop(self):
        """Остановка монитора"""
        self.is_running = False
