import asyncio
import logging
import utils.setup_logging
from utils.filewatcher import FileWatcher
from utils.task_manager import TaskManager, OneShotRunner, PeriodicRunner


async def main():
    config_path = './credentials/credentials.yaml'
    one_shot_runner = None
    periodic_runner = None
    try:
        one_shot_runner = OneShotRunner()
        periodic_runner = PeriodicRunner()
        watcher = FileWatcher(config_path)
        task_manager = TaskManager(config_path, one_shot_runner, periodic_runner)
        await task_manager.add_task_queues_to_runners()
        watcher.add_observer(task_manager)
        await watcher.watch()

    except KeyboardInterrupt:
        logger.info("Получен сигнал прерывания")
        if one_shot_runner is not None:
            await one_shot_runner.stop_all_tasks()
        if periodic_runner is not None:
            await periodic_runner.stop_all_tasks()

    finally:
        logger.info("Приложение завершено")


if __name__ == "__main__":
    utils.setup_logging.setup(level=logging.INFO, log_file='network_monitor.log')
    logger = logging.getLogger("main")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Приложение завершено пользователем")
