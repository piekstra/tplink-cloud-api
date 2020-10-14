from .device_child_action import TPLinkDeviceChildAction

class TPLinkDeviceChildInfo:
    
    def __init__(self, child_info):
        self.id = child_info.get('id')
        self.state = child_info.get('state')
        self.alias = child_info.get('alias')
        self.on_time = child_info.get('on_time')
        self.next_action = TPLinkDeviceChildAction(child_info.get('next_action'))
