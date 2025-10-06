import os
import yaml
from typing import List, Dict, Optional


class DeviceConfigCommands:
    """Класс для управления командами конфигурации устройств"""

    COMMANDS = {
        'cisco': 'show running-config',
        'juniper': 'show configuration',
        'huawei': 'display current-configuration',
        'arista': 'show running-config',
        'mikrotik': 'export'
    }

    @classmethod
    def get_config_command(cls, device: dict) -> str:
        """Получение команды для выгрузки конфигурации устройства"""
        device_type = device.get('device_type')

        if device_type is None:
            raise ValueError("Device type not specified in device dictionary")

        if device_type not in cls.COMMANDS:
            supported_types = ', '.join(cls.get_supported_types())
            raise ValueError(f"Unsupported device type: '{device_type}'. Supported types: {supported_types}")

        return cls.COMMANDS[device_type]


class ConfigManager:
    """Класс для управления конфигурацией"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self._last_modified = 0

    def config_modified(self) -> bool:
        """Проверка изменения конфигурационного файла"""
        try:
            current_modified = os.path.getmtime(self.config_path)
            modified = current_modified > self._last_modified
            if modified:
                self._last_modified = current_modified
            return modified
        except OSError:
            return False

    def load_config(self) -> List[dict]:
        """Загрузка конфигурации"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            devices = config.get('devices', [])
            print(f"Загружено {len(devices)} устройств из конфигурации")
            return devices

        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")
            return []

    def get_config_command(self, device: dict) -> str:
        """Получение команды для устройства"""
        device_type = device.get('device_type', 'cisco')
        return DeviceConfigCommands.get_config_command({'device_type': device_type})

