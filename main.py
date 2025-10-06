import sys
import os

# Добавляем корневую папку проекта в PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

import asyncio
from core.monitor import AdvancedNetworkMonitor


async def main():
    monitor = AdvancedNetworkMonitor(
        poll_interval=60,
        config_check_interval=30
    )

    try:
        await monitor.start_monitoring()

    except KeyboardInterrupt:
        print("\nЗавершение работы монитора...")
    finally:
        monitor.stop()


if __name__ == "__main__":
    asyncio.run(main())
