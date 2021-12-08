from .device_type import TPLinkDeviceType
from .emeter_device import TPLinkEMeterDevice


class HS300ChildAction:
    def __init__(self, child_action):
        self.type = child_action.get('type')
        self.schd_sec = child_action.get('schd_sec')
        self.action = child_action.get('action')


class HS300ChildSysInfo:

    def __init__(self, child_info):
        self.id = child_info.get('id')
        self.state = child_info.get('state')
        self.alias = child_info.get('alias')
        self.on_time = child_info.get('on_time')
        self.next_action = HS300ChildAction(child_info.get('next_action'))


class HS300Child(TPLinkEMeterDevice):

    def __init__(self, client, parent_device_id, child_device_id, device_info):
        super().__init__(
            client,
            parent_device_id,
            device_info,
            child_id=child_device_id
        )
        self.model_type = TPLinkDeviceType.HS300CHILD

    async def get_sys_info(self):
        sys_info = await self._get_sys_info()
        
        if not sys_info:
            print("Something went wrong with your request; please try again")
            return None
        
        return HS300ChildSysInfo(sys_info)
