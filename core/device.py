from enum import Enum, auto


class NetworkDeviceType(Enum):
    """типы сетевых устройств"""
    CISCO_ROUTER = auto()
    CISCO_SWITCH = auto()

    @classmethod
    def from_string(cls, device_type_str: str) -> 'NetworkDeviceType':
        """Сопоставление строки с членом Enum"""
        mapping = {
            'cisco_router': cls.CISCO_ROUTER,
            'cisco_switch': cls.CISCO_SWITCH
        }

        # Приводим к нижнему регистру и ищем в маппинге
        normalized_str = device_type_str.lower().strip()

        if normalized_str in mapping:
            return mapping[normalized_str]
        else:
            raise ValueError(f"Unknown device type: '{device_type_str}'. "
                             f"Supported types: {list(mapping.keys())}")


class DeviceCredentials:
    """Простой класс для хранения учетных данных"""

    def __init__(self, ip: str, username: str, password: str, dev_type: NetworkDeviceType):
        self.ip = ip
        self.username = username
        self.password = password
        self.dev_type = dev_type

    @classmethod
    def from_dict(cls, data: dict) -> 'DeviceCredentials':
        """Конструктор из словаря с проверкой обязательных полей"""
        required_fields = ['ip', 'username', 'password', 'type']
        device_data = data['credentials']
        device_data['type'] = data['type']

        for field in required_fields:
            if field not in device_data:
                raise ValueError(f"Missing required field: {field}")

        return cls(
            ip=str(device_data['ip']),
            username=str(device_data['username']),
            password=str(device_data['password']),
            dev_type=NetworkDeviceType.from_string(device_data['type'])
        )
