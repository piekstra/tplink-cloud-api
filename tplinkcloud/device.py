import asyncio

from .device_type import TPLinkDeviceType
from .device_net_info import DeviceNetInfo
from .device_time import DeviceTime
from .device_timezone import DeviceTimezone
from .device_schedule_rules import DeviceScheduleRules

class DayRuntimeSummary:

    def __init__(self, day_data):
        self.year = day_data.get('year')
        self.month = day_data.get('month')
        self.day = day_data.get('day')
        # Time is in minutes
        self.time = day_data.get('time')

class MonthRuntimeSummary:

    def __init__(self, day_data):
        self.year = day_data.get('year')
        self.month = day_data.get('month')
        # Time is in minutes
        self.minutes = day_data.get('time')

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
    async def get_children(self):
        return None

    # This is expected to be overriden for emeter devices
    def has_emeter(self):
        return False

    def get_alias(self):
        return self.device_info.alias

    # All device requests should go through here
    async def _pass_through_request(self, request_type, sub_request_type, request):
        request_data = {
            request_type: {
                sub_request_type: request
            }
        }
        if self.child_id:
            request_data['context'] = {
                'child_ids': [self.child_id] if self.child_id else None
            }
        response = await self._client.pass_through_request(
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

    async def power_on(self):
        return await self._pass_through_request('system', 'set_relay_state', {'state': 1})

    async def power_off(self):
        return await self._pass_through_request('system', 'set_relay_state', {'state': 0})

    async def toggle(self):
        if await self.is_on():
            await self.power_off()
        else:
            await self.power_on()

    async def _get_sys_info(self):
        return await self._pass_through_request('system', 'get_sysinfo', None)

    # This is intended to be overriden by actual device
    # implementations where sys info is well-defined
    async def get_sys_info(self):
        return await self._get_sys_info()

    async def is_on(self):
        device_sys_info = await self.get_sys_info()
        sys_info = device_sys_info.__dict__ if hasattr(
            device_sys_info, '__dict__') else device_sys_info
        if self.child_id:
            return sys_info['state'] == 1

        return sys_info['relay_state'] == 1

    async def is_off(self):
        device_sys_info = await self.get_sys_info()
        sys_info = device_sys_info.__dict__ if hasattr(
            device_sys_info, '__dict__') else device_sys_info
        if self.child_id:
            return sys_info['state'] == 0

        return sys_info['relay_state'] == 0

    async def set_led_state(self, on):
        # This is intentional - follows the API contract
        led_off_state = 0 if on else 1
        return await self._pass_through_request('set_led_off', 'off', led_off_state)

    async def get_schedule_rules(self):
        schedule_rules = await self._pass_through_request('schedule', 'get_rules', {})
        if schedule_rules is not None:
            return DeviceScheduleRules(schedule_rules)
        return None

    async def get_schedule_rule(self, rule_id):
        schedule = await self.get_schedule_rules()
        if not schedule or not schedule.rules:
            return None

        for rule in schedule.rules:
            if rule.id == rule_id:
                return rule
        
        return None

    async def edit_schedule_rule(self, rule):
        return await self._pass_through_request('schedule', 'edit_rule', rule)
        
    async def add_schedule_rule(self, rule):
        return await self._pass_through_request('schedule', 'add_rule', rule)

    async def delete_all_scheduled_rules(self):
        return await self._pass_through_request('schedule', 'delete_all_rules', None)

    async def delete_schedule_rule(self, rule_id):
        return await self._pass_through_request('schedule', 'delete_rule', {'id': rule_id})

    async def get_runtime_day(self, year, month):
        day_response_data = await self._pass_through_request(
            'schedule', 
            'get_daystat', 
            {
                'year': year,
                'month': month
            }
        )
        # If there is no data for the requested month, data will be None
        if day_response_data and day_response_data.get('err_code') == 0:
            return [DayRuntimeSummary(day_data) for day_data in day_response_data['day_list']]
        return []

    async def get_runtime_month(self, year):
        month_response_data = await self._pass_through_request(
            'schedule', 
            'get_monthstat', 
            {
                'year': year
            }
        )
        # If there is no data for the requested year, data will be None
        if month_response_data and month_response_data.get('err_code') == 0:
            return [MonthRuntimeSummary(month_data) for month_data in month_response_data['month_list']]
        return []

    # Get SSID of network to which the device is connected
    async def get_net_info(self):
        net_info = await self._pass_through_request('netif', 'get_stainfo', None)
        if net_info:
            return DeviceNetInfo(net_info)
        return None

    # Get device current time
    async def get_time(self):
        time = await self._pass_through_request('time', 'get_time', {})
        if time:
            return DeviceTime(time)
        return None

    async def get_timezone(self):
        timezone = await self._pass_through_request('time', 'get_timezone', {})
        if timezone:
            return DeviceTimezone(timezone)
        return None
