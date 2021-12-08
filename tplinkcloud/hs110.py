from .emeter_device import TPLinkEMeterDevice
from .device_type import TPLinkDeviceType
from .hs100 import HS100SysInfo


# The HS110 is an updated version of the HS100 
# that supports emeter capabilities
class HS110SysInfo(HS100SysInfo):

    def __init__(self, sys_info):
        super().__init__(sys_info)


class HS110(TPLinkEMeterDevice):

    def __init__(self, client, device_id, device_info):
        super().__init__(client, device_id, device_info)
        self.model_type = TPLinkDeviceType.HS110

    async def get_sys_info(self):
        sys_info = await self._get_sys_info()
        
        if not sys_info:
            print("Something went wrong with your request; please try again")
            return None
        
        return HS110SysInfo(sys_info)
