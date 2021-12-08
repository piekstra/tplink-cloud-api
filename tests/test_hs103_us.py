import os
import pytest

from tplinkcloud import TPLinkDeviceManager


@pytest.fixture(scope='module')
async def client():
    return await TPLinkDeviceManager(
        username=os.environ.get('TPLINK_KASA_USERNAME'),
        password=os.environ.get('TPLINK_KASA_PASSWORD'),
        prefetch=False,
        cache_devices=False,
        tplink_cloud_api_host=os.environ.get('TPLINK_KASA_API_URL'),
        verbose=False,
        term_id=os.environ.get('TPLINK_KASA_TERM_ID')
    )


@pytest.mark.usefixtures('client')
class TestHS103USDevice(object):

    @pytest.mark.asyncio
    async def test_get_sys_info_gets_info(self, client):
        device_name = 'Bedroom Desk Light'
        device = await client.find_device(device_name)
        sys_info = await device.get_sys_info()

        assert sys_info is not None
        assert sys_info.sw_ver == '1.1.3 Build 200804 Rel.095135'
        assert sys_info.hw_ver == '2.1'
        assert sys_info.model == 'HS103(US)'
        assert sys_info.device_id == '2F50687F0187798768F86EAE340E844A660B2444'
        assert sys_info.oem_id == '349181B1B7F5C59B1E0A932424779904'
        assert sys_info.hw_id == 'AB12E0C542A5202934C7C4183B13970A'
        assert sys_info.rssi == -38
        assert sys_info.longitude_i == 1140579
        assert sys_info.latitude_i == 225431
        assert sys_info.alias == device_name
        assert sys_info.status == 'new'
        assert sys_info.mic_type == 'IOT.SMARTPLUGSWITCH'
        assert sys_info.feature == 'TIM'
        assert sys_info.mac == '11:CE:6A:E6:94:22'
        assert sys_info.updating == 0
        assert sys_info.led_off == 0
        assert sys_info.relay_state == 0
        assert sys_info.on_time == 0
        assert sys_info.active_mode == 'none'
        assert sys_info.icon_hash == ''
        assert sys_info.dev_name == 'Smart Wi-Fi Plug Lite'
        assert sys_info.next_action is not None
        assert sys_info.next_action.action == -1
        assert sys_info.err_code == 0

    @pytest.mark.asyncio
    async def test_has_emeter_returns_false(self, client):
        device_name = 'Bedroom Desk Light'
        device = await client.find_device(device_name)
        has_emeter = device.has_emeter()

        assert has_emeter is not None
        assert has_emeter == False
