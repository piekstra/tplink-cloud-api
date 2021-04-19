import asyncio

from .device_type import TPLinkDeviceType
from .device_net_info import DeviceNetInfo
from .device_time import DeviceTime
from .device_timezone import DeviceTimezone
from .device_schedule_rules import DeviceScheduleRules

class TPLinkDevice:

    def __init__(self, client, device_id, device_info, child_id=None):
        self.device_id = device_id
        self.device_info = device_info
        # child_ids are used for addressing children
        self.child_id = child_id
        self._client = client
        self.model_type = TPLinkDeviceType.UNKNOWN

    # This is expected to be overriden for devices that have children
    def has_children(self):
        return False

    # This is expected to be overriden for devices that have children
    async def get_children_async(self):
        return None

    # This may be overriden for devices that have children
    def get_children(self):
        return asyncio.run(self.get_children_async())

    # This is expected to be overriden for emeter devices
    def has_emeter(self):
        return False

    def get_alias(self):
        return self.device_info.alias

    # All device requests should go through here
    async def _pass_through_request_async(self, request_type, sub_request_type, request):
        request_data = {
            request_type: {
                sub_request_type: request
            }
        }
        if self.child_id:
            request_data['context'] = {
                'child_ids': [self.child_id] if self.child_id else None
            }
        response = await self._client.pass_through_request_async(
            self.device_id, request_data)
        if not response:
            return None

        request_response = response.get(request_type)
        sub_request_response = request_response.get(sub_request_type)
        if self.child_id and sub_request_response.get('children'):
            for child in sub_request_response.get('children'):
                if child.get('id') == self.child_id:
                    return child

        return sub_request_response

    def _pass_through_request(self, request_type, sub_request_type, request):
        return asyncio.run(self._pass_through_request_async(request_type, sub_request_type, request))

    def power_on(self):
        return self._pass_through_request('system', 'set_relay_state', {'state': 1})

    def power_off(self):
        return self._pass_through_request('system', 'set_relay_state', {'state': 0})

    def toggle(self):
        if self.is_on():
            self.power_off()
        else:
            self.power_on()

    async def _get_sys_info_async(self):
        return await self._pass_through_request_async('system', 'get_sysinfo', None)

    def _get_sys_info(self):
        return asyncio.run(self._get_sys_info_async())

    # This is intended to be overriden by actual device
    # implementations where sys info is well-defined
    def get_sys_info(self):
        return self._get_sys_info()

    def is_on(self):
        device_sys_info = self.get_sys_info()
        sys_info = device_sys_info.__dict__ if hasattr(
            device_sys_info, '__dict__') else device_sys_info
        if self.child_id:
            return sys_info['state'] == 1

        return sys_info['relay_state'] == 1

    def is_off(self):
        device_sys_info = self.get_sys_info()
        sys_info = device_sys_info.__dict__ if hasattr(
            device_sys_info, '__dict__') else device_sys_info
        if self.child_id:
            return sys_info['state'] == 0

        return sys_info['relay_state'] == 0

    def set_led_state(self, on):
        # This is intentional - follows the API contract
        led_off_state = 0 if on else 1
        return self._pass_through_request('set_led_off', 'off', led_off_state)

    def get_schedule_rules(self):
        schedule_rules = self._pass_through_request('schedule', 'get_rules', {})
        if schedule_rules is not None:
            return DeviceScheduleRules(schedule_rules)
        return None

    def get_schedule_rule(self, rule_id):
        schedule = self.get_schedule_rules()
        if not schedule or not schedule.rules:
            return None

        for rule in schedule.rules:
            if rule.id == rule_id:
                return rule
        
        return None

    def edit_schedule_rule(self, rule):
        return self._pass_through_request('schedule', 'edit_rule', rule)
        
    def add_schedule_rule(self, rule):
        return self._pass_through_request('schedule', 'add_rule', rule)

    def delete_all_scheduled_rules(self):
        return self._pass_through_request('schedule', 'delete_all_rules', None)

    def delete_schedule_rule(self, rule_id):
        return self._pass_through_request('schedule', 'delete_rule', {'id': rule_id})

    # Get SSID of network to which the device is connected
    def get_net_info(self):
        net_info = self._pass_through_request('netif', 'get_stainfo', None)
        if net_info:
            return DeviceNetInfo(net_info)
        return None

    # Get device current time
    def get_time(self):
        time = self._pass_through_request('time', 'get_time', {})
        if time:
            return DeviceTime(time)
        return None

    def get_timezone(self):
        timezone = self._pass_through_request('time', 'get_timezone', {})
        if timezone:
            return DeviceTimezone(timezone)
        return None
