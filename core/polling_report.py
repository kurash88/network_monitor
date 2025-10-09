import logging
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class NetworkDevicePollStatus:
    host: str
    last_success: Optional[datetime] = None
    last_attempt: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    last_config: Optional[str] = None


class StatusReport:
    """Класс для отслеживания статуса устройств"""
    
    def __init__(self):
        self.device_status: Dict[str, NetworkDevicePollStatus] = {}
        self.logger = logging.getLogger(f"{__name__}.StatusReport")
        self.logger.info("StatusReport инициализирован")

    def update_status(self, host: str, result: Dict):
        """Обновление статуса устройства"""
        if host not in self.device_status:
            self.device_status[host] = NetworkDevicePollStatus(host=host)

        status = self.device_status[host]
        status.last_attempt = datetime.now()

        if isinstance(result, Exception) or (isinstance(result, dict) and not result.get('success')):
            status.failure_count += 1
        else:
            status.success_count += 1
            status.last_success = datetime.now()
            status.last_config = result.get('config')

    def print_status_report(self):
        """Печать отчета о статусе устройств"""
        self.logger.warning("\n" + "=" * 60)
        self.logger.warning("ОТЧЕТ О СТАТУСЕ УСТРОЙСТВ")
        self.logger.warning("=" * 60)

        for host, status in self.device_status.items():
            total_attempts = status.success_count + status.failure_count
            if total_attempts > 0:
                success_rate = (status.success_count / total_attempts) * 100
            else:
                success_rate = 0

            last_success = status.last_success.strftime('%H:%M:%S') if status.last_success else 'НИКОГДА'

            self.logger.warning(f"  {host}:")
            self.logger.warning(f"    Успешно: {status.success_count}, Ошибок: {status.failure_count}")
            self.logger.warning(f"    Успешность: {success_rate:.1f}%")
            self.logger.warning(f"    Последний успех: {last_success}")

        self.logger.warning("=" * 60)
