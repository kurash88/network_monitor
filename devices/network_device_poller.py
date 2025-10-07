import asyncssh
from typing import Dict
from config.network_devices_config_manager import NetworkDevicesConfigManager
from devices.network_device_connector import ConnectionFactory


class NetworkDevicePoller:
    """Класс для сбора конфигурации с устройств"""
    
    def __init__(self, config_manager: NetworkDevicesConfigManager):
        self.config_manager = config_manager
        self.connection_factory = ConnectionFactory()

    async def debug_poll_single_device(self, device: dict) -> Dict:
        """Версия для отладки"""
        try:
            print(f"Starting debug for {device['credentials']['host']}")

            # Точка останова 1 - перед подключением
            host = device['credentials']['host']
            print(f"Host: {host}")

            connector = self.connection_factory.create_connector(device)
            print(f"Connector created: {type(connector)}")

            # Точка останова 2 - во время подключения
            conn = await connector.connect(device)
            print(f"Connected: {conn}")

            command = self.config_manager.get_config_command(device)
            print(f"Command: {command}")

            # Точка останова 3 - во время выполнения команды
            result = await conn.run(command, timeout=30)
            print(f"Result received, length: {len(result.stdout)}")

            # Проверяем, поддерживает ли соединение асинхронное закрытие
            if hasattr(conn, 'close') and callable(getattr(conn, 'close')):
                print(f"Connection has close() method")

                # Проверяем, является ли close() асинхронным
                if hasattr(conn.close, '__await__'):
                    print(f"close() is async method")
                    # Выполняем асинхронное закрытие
                    await conn.close()
                else:
                    print(f"close() is sync method")
                    # Выполняем синхронное закрытие
                    conn.close()
            else:
                print(f"Connection has no close() method")

            return {
                'host': host,
                'config': result.stdout,
                'success': True
            }

        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()  # ← точка останова для исключений
            raise

    async def poll_single_device(self, device: dict) -> Dict:
        """Опрос одного устройства"""
        try:
            connector = self.connection_factory.create_connector(device)
            conn = await connector.connect(device)

            command = self.config_manager.get_config_command(device)
            result = await conn.run(command, timeout=30)
            await conn.close()

            return {
                'host': device['credentials']['host'],
                'config': result.stdout,
                'success': True
            }

        except Exception as e:
            return {
                'host': device['credentials']['host'],
                'success': False,
                'error': str(e)
            }
