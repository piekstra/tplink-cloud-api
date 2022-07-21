from .device_type import TPLinkDeviceType
from .device import TPLinkDevice


class HS105Action:

    def __init__(self, action):
        self.action = action.get('action')


class HS105SysInfo:

    def __init__(self, sys_info):
        self.sw_ver = sys_info.get('sw_ver')
        self.hw_ver = sys_info.get('hw_ver')
        self.type = sys_info.get('type')
        self.model = sys_info.get('model')
        self.mac = sys_info.get('mac')
        self.dev_name = sys_info.get('dev_name')
        self.alias = sys_info.get('alias')
        self.relay_state = sys_info.get('relay_state')
        self.on_time = sys_info.get('on_time')
        self.active_mode = sys_info.get('active_mode')
        self.feature = sys_info.get('feature')
        self.updating = sys_info.get('updating')
        self.icon_hash = sys_info.get('icon_hash')
        self.rssi = sys_info.get('rssi')
        self.led_off = sys_info.get('led_off')
        self.longitude_i = sys_info.get('longitude_i')
        self.latitude_i = sys_info.get('latitude_i')
        self.hw_id = sys_info.get('hwId')
        self.fw_id = sys_info.get('fwId')
        self.device_id = sys_info.get('deviceId')
        self.oem_id = sys_info.get('oemId')
        if 'next_action' in sys_info.keys():
            self.next_action = HS105Action(sys_info.get('next_action'))
        self.err_code = sys_info.get('err_code')


class HS105(TPLinkDevice):

    def __init__(self, client, device_id, device_info):
        super().__init__(client, device_id, device_info)
        self.model_type = TPLinkDeviceType.HS105

    async def get_sys_info(self):
        sys_info = await self._get_sys_info()

        if not sys_info:
            print("Something went wrong with your request; please try again")
            return None
        
        return HS105SysInfo(sys_info)
