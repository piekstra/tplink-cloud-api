import asyncio

from .device_type import TPLinkDeviceType
from .device import TPLinkDevice
from .ep40_child import EP40Child, EP40ChildSysInfo


class EP40SysInfo:

    def __init__(self, sys_info):
        self.sw_ver = sys_info.get('sw_ver')
        self.hw_ver = sys_info.get('hw_ver')
        self.model = sys_info.get('model')
        self.device_id = sys_info.get('deviceId')
        self.oem_id = sys_info.get('oemId')
        self.hw_id = sys_info.get('hwId')
        self.rssi = sys_info.get('rssi')
        self.longitude_i = sys_info.get('longitude_i')
        self.latitude_i = sys_info.get('latitude_i')
        self.alias = sys_info.get('alias')
        self.status = sys_info.get('status')
        self.mic_type = sys_info.get('mic_type')
        self.feature = sys_info.get('feature')
        self.mac = sys_info.get('mac')
        self.updating = sys_info.get('updating')
        self.led_off = sys_info.get('led_off')
        self.children = [EP40ChildSysInfo(child_info)
                         for child_info in sys_info.get('children')]
        self.child_num = sys_info.get('child_num')
        self.err_code = sys_info.get('err_code')


class EP40(TPLinkDevice):

    def __init__(self, client, device_id, device_info):
        super().__init__(client, device_id, device_info)
        self.model_type = TPLinkDeviceType.EP40

    async def get_children_async(self):
        sys_info = await self.get_sys_info()
        children = []
        if sys_info:
            for child_info in sys_info.children:
                device_child = EP40Child(
                    self._client, sys_info.device_id, child_info.id, child_info)
                children.append(device_child)
        return children

    # An override of an identified TPLinkDevice
    def has_children(self):
        return True

    async def get_sys_info(self):
        sys_info = await self._get_sys_info()
        
        if not sys_info:
            print("Something went wrong with your request; please try again")
            return None
        
        return EP40SysInfo(sys_info)

