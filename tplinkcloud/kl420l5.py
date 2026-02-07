from .device_type import TPLinkDeviceType
from .device import TPLinkDevice

_LIGHTING_SERVICE = 'smartlife.iot.smartbulb.lightingservice'


class KL420L5LightState:

    def __init__(self, light_state):
        self.on_off = light_state.get('on_off')
        self.mode = light_state.get('mode')
        self.hue = light_state.get('hue')
        self.saturation = light_state.get('saturation')
        self.color_temp = light_state.get('color_temp')
        self.brightness = light_state.get('brightness')


class KL420L5SysInfo:

    def __init__(self, sys_info):
        self.sw_ver = sys_info.get('sw_ver')
        self.hw_ver = sys_info.get('hw_ver')
        self.model = sys_info.get('model')
        self.device_id = sys_info.get('deviceId')
        self.oem_id = sys_info.get('oemId')
        self.hw_id = sys_info.get('hwId')
        self.rssi = sys_info.get('rssi')
        self.longitude_i = sys_info.get('longitude_i')
        self.latitude_i = sys_info.get('latitude_i')
        self.alias = sys_info.get('alias')
        self.status = sys_info.get('status')
        self.mic_type = sys_info.get('mic_type')
        self.feature = sys_info.get('feature')
        self.mac = sys_info.get('mac')
        self.updating = sys_info.get('updating')
        self.led_off = sys_info.get('led_off')
        self.is_dimmable = sys_info.get('is_dimmable')
        self.is_color = sys_info.get('is_color')
        self.is_variable_color_temp = sys_info.get('is_variable_color_temp')
        light_state = sys_info.get('light_state', {})
        self.light_state = KL420L5LightState(light_state)
        self.relay_state = light_state.get('on_off', 0)
        self.err_code = sys_info.get('err_code')


class KL420L5(TPLinkDevice):

    def __init__(self, client, device_id, device_info):
        super().__init__(client, device_id, device_info)
        self.model_type = TPLinkDeviceType.KL420L5

    async def get_sys_info(self):
        sys_info = await self._get_sys_info()

        if not sys_info:
            print("Something went wrong with your request; please try again")
            return None

        return KL420L5SysInfo(sys_info)

    async def get_light_state(self):
        return await self._pass_through_request(
            _LIGHTING_SERVICE, 'get_light_state', {})

    async def set_light_state(self, on_off=None, brightness=None, hue=None,
                              saturation=None, color_temp=None,
                              transition_period=None):
        state = {}
        if on_off is not None:
            state['on_off'] = on_off
        if brightness is not None:
            state['brightness'] = brightness
        if hue is not None:
            state['hue'] = hue
        if saturation is not None:
            state['saturation'] = saturation
        if color_temp is not None:
            state['color_temp'] = color_temp
        if transition_period is not None:
            state['transition_period'] = transition_period
        return await self._pass_through_request(
            _LIGHTING_SERVICE, 'transition_light_state', state)

    async def power_on(self):
        return await self.set_light_state(on_off=1)

    async def power_off(self):
        return await self.set_light_state(on_off=0)

    async def set_brightness(self, brightness):
        return await self.set_light_state(on_off=1, brightness=brightness)

    async def set_color(self, hue, saturation, brightness=None):
        return await self.set_light_state(
            on_off=1, hue=hue, saturation=saturation, color_temp=0,
            brightness=brightness)

    async def set_color_temp(self, color_temp, brightness=None):
        return await self.set_light_state(
            on_off=1, color_temp=color_temp, brightness=brightness)

    async def is_on(self):
        sys_info = await self.get_sys_info()
        if sys_info is None:
            return None
        return sys_info.light_state.on_off == 1

    async def is_off(self):
        sys_info = await self.get_sys_info()
        if sys_info is None:
            return None
        return sys_info.light_state.on_off == 0
