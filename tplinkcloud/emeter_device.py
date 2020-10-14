from .device import TPLinkDevice

class TPLinkEMeterDevice(TPLinkDevice):

    def __init__(self, client, device_id, device_info, child_id=None):
        super().__init__(client, device_id, device_info, child_id)

    def get_power_usage_realtime(self):
        return self._pass_through_request('emeter', 'get_realtime', None)
    
    def get_power_usage_day(self, year, month):
        return self._pass_through_request(
            'emeter', 
            'get_daystat', 
            { 
                'year': year,
                'month': month
            }
        )

    def get_power_usage_month(self, year):
        return self._pass_through_request(
            'emeter',
            'get_monthstat',
            { 
                'year': year
            }
        )