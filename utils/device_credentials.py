class DeviceCredentials:
    def __init__(self, ip: str, username: str, password: str, dev_type: str, watch: bool = False):
        self.ip = ip
        self.username = username
        self.password = password
        self.dev_type = dev_type
        self.watch = watch