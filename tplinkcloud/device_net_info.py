class DeviceNetInfo:

    def __init__(self, net_info):
        # This should be the name of your network
        self.ssid = net_info.get('ssid')
        self.key_type = net_info.get('key_type')
        self.rssi = net_info.get('rssi')
        self.err_code = net_info.get('err_code')
