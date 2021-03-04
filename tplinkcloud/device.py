from .device_type import TPLinkDeviceType


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
    def get_children(self):
        return None

    def get_alias(self):
        return self.device_info.alias

    # All device requests should go through here
    def _pass_through_request(self, request_type, sub_request_type, request):
        request_data = {
            request_type: {
                sub_request_type: request
            }
        }
        if self.child_id:
            request_data['context'] = {
                'child_ids': [self.child_id] if self.child_id else None
            }
        response = self._client.pass_through_request(
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

    def power_on(self):
        return self._pass_through_request('system', 'set_relay_state', {'state': 1})

    def power_off(self):
        return self._pass_through_request('system', 'set_relay_state', {'state': 0})

    def toggle(self):
        if self.is_on():
            self.power_off()
        else:
            self.power_on()

    def _get_sys_info(self):
        return self._pass_through_request('system', 'get_sysinfo', None)

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
        return self._pass_through_request('schedule', 'get_rules', {})

    def edit_schedule_rule(self, rule):
        return self._pass_through_request('schedule', 'edit_rule', rule)
