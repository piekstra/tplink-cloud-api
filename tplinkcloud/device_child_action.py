class TPLinkDeviceChildAction:
    
    def __init__(self, child_action):
        self.type = child_action.get('type')
        self.schd_sec = child_action.get('schd_sec')
        self.action = child_action.get('action')
