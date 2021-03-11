from .device_type import TPLinkDeviceType
from .emeter_device import TPLinkEMeterDevice


class HS100Action:

    def __init__(self, action):
        self.type = action.get('type')


class HS100SysInfo:

    def __init__(self, sys_info):
        self.err_code = sys_info.get('err_code')
        self.sw_ver = sys_info.get('sw_ver')
        self.hw_ver = sys_info.get('hw_ver')
        self.type = sys_info.get('type')
        self.model = sys_info.get('model')
        self.mac = sys_info.get('mac')
        self.device_id = sys_info.get('deviceId')
        self.hw_id = sys_info.get('hwId')
        self.fw_id = sys_info.get('fwId')
        self.oem_id = sys_info.get('oemId')
        self.alias = sys_info.get('alias')
        self.dev_name = sys_info.get('dev_name')
        self.icon_hash = sys_info.get('icon_hash')
        self.relay_state = sys_info.get('relay_state')
        self.on_time = sys_info.get('on_time')
        self.active_mode = sys_info.get('active_mode')
        self.feature = sys_info.get('feature')
        self.updating = sys_info.get('updating')
        self.rssi = sys_info.get('rssi')
        self.led_off = sys_info.get('led_off')
        self.latitude = sys_info.get('latitude')
        self.longitude = sys_info.get('longitude')


class HS100(TPLinkEMeterDevice):

    def __init__(self, client, device_id, device_info):
        super().__init__(client, device_id, device_info)
        self.model_type = TPLinkDeviceType.HS100

    def get_sys_info(self):
        sys_info = self._get_sys_info()
        
        if not sys_info:
            print("Something went wrong with your request; please try again")
            return None
        
        return HS100SysInfo(sys_info)
