import logging
import yaml
from typing import List
from core.device import DeviceCredentials


class DevicesCredentialsParser:
    """Класс для управления конфигурацией"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self._last_modified = 0

        self.logger = logging.getLogger(f"{__name__}.DevicesCredentialsParser")
        self.logger.info("DevicesCredentialsParser инициализирован")

    def load_polling_network_device_credentials(self) -> List[DeviceCredentials]:
        """Загрузка конфигурации"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            devices = config.get('devices', [])
            credentials = [DeviceCredentials.from_dict(device) for device in devices]
            self.logger.debug(f"Загружено {len(credentials)} credentials из конфигурации")
            return credentials

        except Exception as e:
            self.logger.exception(f"Ошибка загрузки конфигурации: {e}")
            return []


