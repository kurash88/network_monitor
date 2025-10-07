import asyncssh
from abc import ABC, abstractmethod
from typing import Dict


class DeviceConnector(ABC):
    """Абстрактный класс для подключения к устройствам"""
    
    @abstractmethod
    async def connect(self, device: dict) -> asyncssh.SSHClientConnection:
        pass


class DirectConnector(DeviceConnector):
    """Прямое подключение к устройству"""
    
    async def connect(self, device: dict) -> asyncssh.SSHClientConnection:
        return await asyncssh.connect(
            device['credentials']['host'],
            username=device['credentials']['username'],
            password=device['credentials']['password'],
            known_hosts=None,
            connect_timeout=30
        )


"""класс на будущее со схемой с jump хостами
TODO проверить несколько jump хостов"""
class JumpHostConnector(DeviceConnector):
    """Подключение через jump host"""
    
    async def connect(self, device: dict) -> asyncssh.SSHClientConnection:
        # Подключаемся к jump host
        jump_conn = await asyncssh.connect(
            device['jump_host'],
            username=device['jump_credentials']['username'],
            password=device['jump_credentials']['password'],
            known_hosts=None,
            connect_timeout=30
        )

        # Подключаемся к целевому устройству через туннель
        target_conn = await asyncssh.connect(
            device['host'],
            username=device['credentials']['username'],
            password=device['credentials']['password'],
            tunnel=jump_conn,
            known_hosts=None,
            connect_timeout=30
        )

        return target_conn

"""фабрика для дальнейшего использования с jump хостами в т.ч. больше одного уровня вложенности"""
class ConnectionFactory:
    """Фабрика для создания подключений"""
    
    @staticmethod
    def create_connector(device: dict) -> DeviceConnector:
        if 'jump_host' in device:
            return JumpHostConnector()
        return DirectConnector()
