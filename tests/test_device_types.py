import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tplinkcloud.device_type import TPLinkDeviceType
from tplinkcloud.device import TPLinkDevice
from tplinkcloud.hs200 import HS200, HS200SysInfo
from tplinkcloud.kp200 import KP200, KP200SysInfo
from tplinkcloud.kp200_child import KP200Child, KP200ChildSysInfo
from tplinkcloud.kp400 import KP400, KP400SysInfo
from tplinkcloud.kp400_child import KP400Child, KP400ChildSysInfo
from tplinkcloud.kl420l5 import KL420L5, KL420L5SysInfo
from tplinkcloud.kl430 import KL430, KL430SysInfo


def _mock_client():
    client = MagicMock()
    client.pass_through_request = AsyncMock()
    return client


def _device_info(model='HS200(US)', alias='Test'):
    info = MagicMock()
    info.device_model = model
    info.alias = alias
    info.device_id = 'test_id'
    info.app_server_url = 'http://test'
    return info


class TestHS200:

    def test_model_type(self):
        device = HS200(_mock_client(), 'id', _device_info())
        assert device.model_type == TPLinkDeviceType.HS200

    @pytest.mark.asyncio
    async def test_get_sys_info(self):
        client = _mock_client()
        device = HS200(client, 'id', _device_info())
        client.pass_through_request.return_value = {
            'system': {
                'get_sysinfo': {
                    'relay_state': 1,
                    'alias': 'Front Door',
                    'model': 'HS200(US)',
                    'sw_ver': '1.0',
                    'hw_ver': '3.0',
                    'next_action': {'type': -1},
                    'err_code': 0,
                }
            }
        }

        # _get_sys_info extracts the inner dict
        with patch.object(device, '_get_sys_info', new_callable=AsyncMock) as mock:
            mock.return_value = {
                'relay_state': 1,
                'alias': 'Front Door',
                'model': 'HS200(US)',
                'next_action': {'type': -1},
                'err_code': 0,
            }
            result = await device.get_sys_info()

        assert isinstance(result, HS200SysInfo)
        assert result.relay_state == 1
        assert result.alias == 'Front Door'


class TestKP200:

    def test_model_type(self):
        device = KP200(_mock_client(), 'id', _device_info('KP200(US)'))
        assert device.model_type == TPLinkDeviceType.KP200

    def test_has_children(self):
        device = KP200(_mock_client(), 'id', _device_info('KP200(US)'))
        assert device.has_children() is True

    @pytest.mark.asyncio
    async def test_get_children_async(self):
        client = _mock_client()
        device = KP200(client, 'parent_id', _device_info('KP200(US)'))

        with patch.object(device, '_get_sys_info', new_callable=AsyncMock) as mock:
            mock.return_value = {
                'deviceId': 'parent_id',
                'children': [
                    {'id': 'child_00', 'state': 1, 'alias': 'Outlet 1',
                     'on_time': 100, 'next_action': {'type': -1}},
                    {'id': 'child_01', 'state': 0, 'alias': 'Outlet 2',
                     'on_time': 0, 'next_action': {'type': -1}},
                ],
                'child_num': 2,
                'err_code': 0,
            }
            children = await device.get_children_async()

        assert len(children) == 2
        assert isinstance(children[0], KP200Child)
        assert children[0].model_type == TPLinkDeviceType.KP200CHILD


class TestKP400:

    def test_model_type(self):
        device = KP400(_mock_client(), 'id', _device_info('KP400(US)'))
        assert device.model_type == TPLinkDeviceType.KP400

    def test_has_children(self):
        device = KP400(_mock_client(), 'id', _device_info('KP400(US)'))
        assert device.has_children() is True


class TestKL420L5:

    def test_model_type(self):
        device = KL420L5(_mock_client(), 'id', _device_info('KL420L5(US)'))
        assert device.model_type == TPLinkDeviceType.KL420L5

    def test_has_no_children(self):
        device = KL420L5(_mock_client(), 'id', _device_info('KL420L5(US)'))
        assert device.has_children() is False

    @pytest.mark.asyncio
    async def test_power_on_uses_lighting_service(self):
        client = _mock_client()
        device = KL420L5(client, 'id', _device_info('KL420L5(US)'))

        with patch.object(device, '_pass_through_request', new_callable=AsyncMock) as mock:
            await device.power_on()
            mock.assert_called_once_with(
                'smartlife.iot.smartbulb.lightingservice',
                'transition_light_state',
                {'on_off': 1}
            )

    @pytest.mark.asyncio
    async def test_set_color(self):
        client = _mock_client()
        device = KL420L5(client, 'id', _device_info('KL420L5(US)'))

        with patch.object(device, '_pass_through_request', new_callable=AsyncMock) as mock:
            await device.set_color(hue=240, saturation=100, brightness=75)
            mock.assert_called_once_with(
                'smartlife.iot.smartbulb.lightingservice',
                'transition_light_state',
                {'on_off': 1, 'hue': 240, 'saturation': 100,
                 'color_temp': 0, 'brightness': 75}
            )

    @pytest.mark.asyncio
    async def test_set_color_temp(self):
        client = _mock_client()
        device = KL420L5(client, 'id', _device_info('KL420L5(US)'))

        with patch.object(device, '_pass_through_request', new_callable=AsyncMock) as mock:
            await device.set_color_temp(color_temp=4000)
            mock.assert_called_once_with(
                'smartlife.iot.smartbulb.lightingservice',
                'transition_light_state',
                {'on_off': 1, 'color_temp': 4000}
            )

    @pytest.mark.asyncio
    async def test_is_on(self):
        device = KL420L5(_mock_client(), 'id', _device_info('KL420L5(US)'))
        with patch.object(device, '_get_sys_info', new_callable=AsyncMock) as mock:
            mock.return_value = {
                'light_state': {'on_off': 1, 'brightness': 50},
                'err_code': 0,
            }
            assert await device.is_on() is True
            assert await device.is_off() is False


class TestKL430:

    def test_model_type(self):
        device = KL430(_mock_client(), 'id', _device_info('KL430(US)'))
        assert device.model_type == TPLinkDeviceType.KL430

    @pytest.mark.asyncio
    async def test_set_brightness(self):
        client = _mock_client()
        device = KL430(client, 'id', _device_info('KL430(US)'))

        with patch.object(device, '_pass_through_request', new_callable=AsyncMock) as mock:
            await device.set_brightness(50)
            mock.assert_called_once_with(
                'smartlife.iot.smartbulb.lightingservice',
                'transition_light_state',
                {'on_off': 1, 'brightness': 50}
            )


class TestDeviceTypeEnum:

    def test_all_new_types_exist(self):
        assert TPLinkDeviceType.HS200.value == 200
        assert TPLinkDeviceType.KP200.value == 2000
        assert TPLinkDeviceType.KP200CHILD.value == 2001
        assert TPLinkDeviceType.KP400.value == 4001
        assert TPLinkDeviceType.KP400CHILD.value == 4002
        assert TPLinkDeviceType.KL420L5.value == 420
        assert TPLinkDeviceType.KL430.value == 430
