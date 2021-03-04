class TPLinkDeviceInfo:

    def __init__(self, device_info):
        self.device_type = device_info.get('deviceType')
        self.role = device_info.get('role')
        self.fw_ver = device_info.get('fwVer')
        self.app_server_url = device_info.get('appServerUrl')
        self.device_region = device_info.get('deviceRegion')
        self.device_id = device_info.get('deviceId')
        self.device_name = device_info.get('deviceName')
        self.device_hw_ver = device_info.get('deviceHwVer')
        self.alias = device_info.get('alias')
        self.device_mac = device_info.get('deviceMac')
        self.oem_id = device_info.get('oemId')
        self.device_model = device_info.get('deviceModel')
        self.hw_id = device_info.get('hwId')
        self.fw_id = device_info.get('fwId')
        self.is_same_region = device_info.get('isSameRegion')
        self.status = device_info.get('status')
