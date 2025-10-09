from core.device import NetworkDeviceType


class ExtractConfigFromDeviceCommands:
    """Класс для управления командами конфигурации устройств"""

    COMMANDS = {
        NetworkDeviceType.CISCO_ROUTER: 'show running-config',
        NetworkDeviceType.CISCO_SWITCH: 'show running-config'
    }

    @classmethod
    def get_extract_command(cls, device_type: NetworkDeviceType) -> str:
        """Получение команды для выгрузки конфигурации устройства"""

        if device_type is None:
            raise ValueError("Device type not specified")

        return cls.COMMANDS[device_type]