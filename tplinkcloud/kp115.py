from .device_type import TPLinkDeviceType
from .hs110 import HS110, HS110SysInfo


class KP115SysInfo(HS110SysInfo):

    def __init__(self, sys_info):
        super().__init__(sys_info)


class KP115(HS110):

    def __init__(self, client, device_id, device_info):
        super().__init__(client, device_id, device_info)
        self.model_type = TPLinkDeviceType.KP115

    def get_sys_info(self):
        sys_info = self._get_sys_info()
        
        if not sys_info:
            print("Something went wrong with your request; please try again")
            return None
        
        return KP115SysInfo(sys_info)
