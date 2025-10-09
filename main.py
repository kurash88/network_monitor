import asyncio
import logging
import sys

from core.start_stop import AdvancedNetworkMonitor


def setup_logging(level=logging.INFO, log_file=None):
    """Настройка логирования один раз при старте приложения"""

    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

    logging.getLogger('asyncssh').setLevel(logging.WARNING)  # уменьшаем шум asyncssh


async def main():
    setup_logging(level=logging.WARNING, log_file='network_monitor.log')
    logger = logging.getLogger("main")
    try:
        monitor = AdvancedNetworkMonitor(
            poll_interval=60,
            config_check_interval=30
        )

        # Проверяем, что монитор корректно инициализирован
        if not hasattr(monitor, 'is_running') or not monitor.is_running:
            logger.error("Монитор не был корректно инициализирован")
            return

        await monitor.start_monitoring()

    except Exception as e:
        logger.exception(f"Ошибка инициализации монитора: {e}")
        return
    except KeyboardInterrupt:
        logger.exception("\nЗавершение работы монитора...")
    finally:
        if 'monitor' in locals():
            monitor.stop()


if __name__ == "__main__":
    asyncio.run(main())
