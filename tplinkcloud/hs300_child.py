from .device_type import TPLinkDeviceType
from .emeter_device import TPLinkEMeterDevice

class HS300Child(TPLinkEMeterDevice):

    def __init__(self, client, parent_device_id, child_device_id, device_info):
        super().__init__(
            client, 
            parent_device_id,
            device_info, 
            child_id=child_device_id
        )
        self.model_type = TPLinkDeviceType.HS300CHILD

