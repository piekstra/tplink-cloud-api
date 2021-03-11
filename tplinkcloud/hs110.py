from .device_type import TPLinkDeviceType
from .hs100 import HS100, HS100SysInfo


class HS110SysInfo(HS100SysInfo):

    def __init__(self, sys_info):
        super().__init__(sys_info)


class HS110(HS100):

    def __init__(self, client, device_id, device_info):
        super().__init__(client, device_id, device_info)
        self.model_type = TPLinkDeviceType.HS110

    def get_sys_info(self):
        sys_info = self._get_sys_info()
        
        if not sys_info:
            print("Something went wrong with your request; please try again")
            return None
        
        return HS110SysInfo(sys_info)
