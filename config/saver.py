import os
from difflib import Differ
from datetime import datetime
from typing import Optional


class ConfigSaver:
    """Класс для сохранения конфигураций"""
    
    def __init__(self, config_dir: str = 'configs'):
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)

    @staticmethod
    def show_diff_colored(latest_config, new_config):
        latest_lines = latest_config.splitlines()
        new_lines = new_config.splitlines()

        d = Differ()
        diff = list(d.compare(latest_lines, new_lines))

        print("🔍 Разница между конфигурациями:")
        for line in diff:
            if line.startswith('+ '):
                print(f"\033[92m{line}\033[0m")  # Зеленый - добавленные строки
            elif line.startswith('- '):
                print(f"\033[91m{line}\033[0m")  # Красный - удаленные строки
            elif line.startswith('? '):
                print(f"\033[93m{line}\033[0m")  # Желтый - изменения
            else:
                print(line)  # Без изменений
    async def save_config_if_changed(self, host: str, new_config: str):
        """Сохраняет конфигурацию только если она изменилась"""
        try:
            latest_config = self._get_latest_config(host)

            if latest_config != new_config or latest_config is None:
                """debug"""
                if latest_config is not None:
                    if len(latest_config) > 0:
                        self.show_diff_colored(latest_config, new_config)

                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{self.config_dir}/{host}_{timestamp}.cfg"

                with open(filename, 'w', newline='') as f:
                    f.write(new_config)

                print(f"Конфигурация {host} сохранена (изменения обнаружены)")
            else:
                print(f"Конфигурация {host} не изменилась")

        except Exception as e:
            print(f"Ошибка сохранения конфигурации {host}: {e}")

    def _get_latest_config(self, host: str) -> Optional[str]:
        """Получение последней сохраненной конфигурации"""
        try:
            for filename in os.listdir(self.config_dir):
                if filename.startswith(f"{host}_"):
                    with open(os.path.join(self.config_dir, filename), 'r', newline='') as f:
                        return f.read()
        except Exception:
            pass
        return None
