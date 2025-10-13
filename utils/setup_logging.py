import logging
import sys


# Настройка логирования
def setup(level=logging.INFO, log_file=None):
    """Настройка логирования один раз при старте приложения"""

    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )

    logging.getLogger('asyncssh').setLevel(logging.WARNING)
