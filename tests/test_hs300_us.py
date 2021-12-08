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
class TestHS300USDevice(object):

    @pytest.mark.asyncio
    async def test_get_sys_info_gets_info(self, client):
        device_name = 'TP-LINK_Power Strip_9704'
        device = await client.find_device(device_name)
        print(device.get_alias())
        sys_info = await device.get_sys_info()

        assert sys_info is not None
        assert sys_info.sw_ver == '1.0.19 Build 200224 Rel.090814'
        assert sys_info.hw_ver == '1.0'
        assert sys_info.model == 'HS300(US)'
        assert sys_info.device_id == '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E'
        assert sys_info.oem_id == 'C20341B1E3455640F77F93C8286CD3E3'
        assert sys_info.hw_id == 'F0209F82A6A831CA4AD1CEE3FE574BA2'
        assert sys_info.rssi == -38
        assert sys_info.longitude_i == 1140579
        assert sys_info.latitude_i == 225431
        assert sys_info.alias == device_name
        assert sys_info.status == 'new'
        assert sys_info.mic_type == 'IOT.SMARTPLUGSWITCH'
        assert sys_info.feature == 'TIM:ENE'
        assert sys_info.mac == '28:A6:9C:74:BA:90'
        assert sys_info.updating == 0
        assert sys_info.led_off == 0
        assert sys_info.child_num == 6
        assert sys_info.err_code == 0

        assert sys_info.children is not None
        assert len(sys_info.children) == 6
        assert sys_info.children[0].id == '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E00'
        assert sys_info.children[0].state == 0
        assert sys_info.children[0].alias == 'Plug 1'
        assert sys_info.children[0].on_time == 0
        assert sys_info.children[0].next_action is not None
        assert sys_info.children[0].next_action.type == -1
        assert sys_info.children[0].next_action.schd_sec is None
        assert sys_info.children[0].next_action.action is None
        assert sys_info.children[1].id == '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E01'
        assert sys_info.children[1].state == 0
        assert sys_info.children[1].alias == 'Plug 2'
        assert sys_info.children[1].on_time == 0
        assert sys_info.children[1].next_action is not None
        assert sys_info.children[1].next_action.type == -1
        assert sys_info.children[1].next_action.schd_sec is None
        assert sys_info.children[1].next_action.action is None
        assert sys_info.children[2].id == '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E02'
        assert sys_info.children[2].state == 1
        assert sys_info.children[2].alias == 'Plug 3'
        assert sys_info.children[2].on_time == 65581
        assert sys_info.children[2].next_action is not None
        assert sys_info.children[2].next_action.type == -1
        assert sys_info.children[2].next_action.schd_sec is None
        assert sys_info.children[2].next_action.action is None
        assert sys_info.children[3].id == '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E03'
        assert sys_info.children[3].state == 0
        assert sys_info.children[3].alias == 'Plug 4'
        assert sys_info.children[3].on_time == 0
        assert sys_info.children[3].next_action is not None
        assert sys_info.children[3].next_action.type == -1
        assert sys_info.children[3].next_action.schd_sec is None
        assert sys_info.children[3].next_action.action is None
        assert sys_info.children[4].id == '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E04'
        assert sys_info.children[4].state == 0
        assert sys_info.children[4].alias == 'Plug 5'
        assert sys_info.children[4].on_time == 0
        assert sys_info.children[4].next_action is not None
        assert sys_info.children[4].next_action.type == -1
        assert sys_info.children[4].next_action.schd_sec is None
        assert sys_info.children[4].next_action.action is None
        assert sys_info.children[5].id == '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E05'
        assert sys_info.children[5].state == 1
        assert sys_info.children[5].alias == 'Plug 6'
        assert sys_info.children[5].on_time == 65581
        assert sys_info.children[5].next_action is not None
        assert sys_info.children[5].next_action.type == -1
        assert sys_info.children[5].next_action.schd_sec is None
        assert sys_info.children[5].next_action.action is None

    @pytest.mark.asyncio
    async def test_has_emeter_returns_false_for_parent(self, client):
        device_name = 'TP-LINK_Power Strip_9704'
        parent_device = await client.find_device(device_name)
        has_emeter = parent_device.has_emeter()

        assert has_emeter is not None
        assert has_emeter == False

    @pytest.mark.asyncio
    async def test_has_emeter_returns_true_for_child(self, client):
        device_name = 'Plug 6'
        child_device = await client.find_device(device_name)
        has_emeter = child_device.has_emeter()

        assert has_emeter is not None
        assert has_emeter == True
