import aiofiles
import asyncssh

import logging
from utils.config import DeviceCredentials

logger = logging.getLogger("device")


async def process_device(cred: DeviceCredentials):
    """Однократная обработка устройства"""
    try:
        logger.info(f"начат опрос {cred.ip}")
        async with asyncssh.connect(
                cred.ip,
                username=cred.username,
                password=cred.password,
                known_hosts=None,
                connect_timeout=10
        ) as conn:
            result = await conn.run('show running-config')
            async with aiofiles.open(f"{cred.ip}.txt", 'w') as f:
                await f.write(result.stdout)
            logger.info(f"{cred.ip} - конфигурация сохранена")

    except Exception as e:
        logger.error(f"{cred.ip} - ошибка: {e}")
