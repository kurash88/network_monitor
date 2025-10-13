from typing import List, Dict

import yaml
import aiofiles
import logging

from utils.device_credentials import DeviceCredentials

logger = logging.getLogger("device")


async def get_config_contents(file_path: str) -> str:
    """Асинхронная загрузка конфигурации"""
    try:
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
            return content
    except Exception as e:
        logger.error(f"Ошибка чтения конфигурационного файла: {e}")


def yaml_to_credentials(content: str) -> List[DeviceCredentials]:
    devices = yaml.safe_load(content).get('devices', [])
    credentials = []
    for i, device in enumerate(devices):
        dev_data = device.get('credentials', {})
        dev_data['type'] = device.get('type', '')

        if not dev_data:
            raise ValueError(f"Device #{i}: Missing 'credentials' section")

        required = ['ip', 'username', 'password', 'type']
        missing_fields = []
        empty_fields = []

        for field in required:
            if field not in dev_data:
                missing_fields.append(field)
            elif not dev_data[field]:
                empty_fields.append(field)

        errors = []
        if missing_fields:
            errors.append(f"missing fields: {missing_fields}")
        if empty_fields:
            errors.append(f"empty fields: {empty_fields}")

        if errors:
            raise ValueError(f"Device #{i}: {', '.join(errors)}. Device data: {dev_data}")

        # Преобразуем watch
        watch_value = dev_data.get('watch', False)
        watch_bool = watch_value and str(watch_value).lower() in ('true', 'yes', '1', 'on')

        credentials.append(DeviceCredentials(
            ip=str(dev_data['ip']),
            username=str(dev_data['username']),
            password=str(dev_data['password']),
            dev_type=str(dev_data['type']),
            watch=bool(watch_bool)
        ))

    return credentials
