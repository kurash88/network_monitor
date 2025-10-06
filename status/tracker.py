from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class DeviceStatus:
    host: str
    last_success: Optional[datetime] = None
    last_attempt: Optional[datetime] = None
    success_count: int = 0
    failure_count: int = 0
    last_config: Optional[str] = None


class StatusTracker:
    """Класс для отслеживания статуса устройств"""
    
    def __init__(self):
        self.device_status: Dict[str, DeviceStatus] = {}

    def update_status(self, host: str, result: Dict):
        """Обновление статуса устройства"""
        if host not in self.device_status:
            self.device_status[host] = DeviceStatus(host=host)

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
        print("\n" + "=" * 60)
        print("ОТЧЕТ О СТАТУСЕ УСТРОЙСТВ")
        print("=" * 60)

        for host, status in self.device_status.items():
            total_attempts = status.success_count + status.failure_count
            if total_attempts > 0:
                success_rate = (status.success_count / total_attempts) * 100
            else:
                success_rate = 0

            last_success = status.last_success.strftime('%H:%M:%S') if status.last_success else 'НИКОГДА'

            print(f"  {host}:")
            print(f"    Успешно: {status.success_count}, Ошибок: {status.failure_count}")
            print(f"    Успешность: {success_rate:.1f}%")
            print(f"    Последний успех: {last_success}")

        print("=" * 60)
