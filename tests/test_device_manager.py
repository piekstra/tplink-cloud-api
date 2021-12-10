import os
import pytest
import asyncio

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


@pytest.mark.usefixtures('client', 'event_loop')
class TestGetDevices(object):

    @pytest.mark.asyncio
    async def test_gets_devices(self, client):
        device_list = await client.get_devices()
        assert device_list is not None
        # 5 devices but the 5th one has 6 children
        assert len(device_list) == 11

@pytest.mark.usefixtures('client')
class TestFindDevice(object):

    @pytest.mark.asyncio
    async def test_finds_hs103_us_device(self, client):
        device_name = 'Bedroom Desk Light'
        device_id = '2F50687F0187798768F86EAE340E844A660B2444'
        device = await client.find_device(device_name)

        assert device is not None
        assert device.get_alias() == device_name
        assert device.device_id == device_id
        assert device.device_info is not None
        assert device.device_info.device_type == 'IOT.SMARTPLUGSWITCH'
        assert device.device_info.role == 0
        assert device.device_info.fw_ver == '1.1.3 Build 200804 Rel.095135'
        assert device.device_info.app_server_url == 'http://127.0.0.1:8080'
        assert device.device_info.device_region == 'us-east-1'
        assert device.device_info.device_id == device_id
        assert device.device_info.device_name == 'Smart Wi-Fi Plug Lite'
        assert device.device_info.device_hw_ver == '2.1'
        assert device.device_info.alias == device_name
        assert device.device_info.device_mac == '11CE6AE69422'
        assert device.device_info.oem_id == '349181B1B7F5C59B1E0A932424779904'
        assert device.device_info.device_model == 'HS103(US)'
        assert device.device_info.hw_id == 'AB12E0C542A5202934C7C4183B13970A'
        assert device.device_info.fw_id == '00000000000000000000000000000000'
        assert device.device_info.is_same_region is True
        assert device.device_info.status == 1
        assert device.child_id is None
        # We can cheat a little with knowledge that this is an enum
        assert device.model_type is not None
        assert device.model_type.name == 'HS103'

    @pytest.mark.asyncio
    async def test_finds_hs105_us_device(self, client):
        device_name = 'Left Lamp'
        device_id = '9F231AD114D92FE98DEB7843ADC91D0EEEF2D0B8'
        device = await client.find_device(device_name)

        assert device is not None
        assert device.get_alias() == device_name
        assert device.device_id == device_id
        assert device.device_info is not None
        assert device.device_info.device_type == 'IOT.SMARTPLUGSWITCH'
        assert device.device_info.role == 0
        assert device.device_info.fw_ver == '1.5.6 Build 191114 Rel.104204'
        assert device.device_info.app_server_url == 'http://127.0.0.1:8080'
        assert device.device_info.device_region == 'us-east-1'
        assert device.device_info.device_id == device_id
        assert device.device_info.device_name == 'Smart Wi-Fi Plug Mini'
        assert device.device_info.device_hw_ver == '1.0'
        assert device.device_info.alias == device_name
        assert device.device_info.device_mac == 'D2A8326B0871'
        assert device.device_info.oem_id == 'EDC2878EAA7AF9F1812E945E048F2AD5'
        assert device.device_info.device_model == 'HS105(US)'
        assert device.device_info.hw_id == '7E041C9693106D65C4254EA0E4C01E1A'
        assert device.device_info.fw_id == '00000000000000000000000000000000'
        assert device.device_info.is_same_region is True
        assert device.device_info.status == 1
        assert device.child_id is None
        # We can cheat a little with knowledge that this is an enum
        assert device.model_type is not None
        assert device.model_type.name == 'HS105'

    @pytest.mark.asyncio
    async def test_finds_hs110_us_device(self, client):
        device_name = 'Bedroom Light'
        device_id = '6572495E336088D1DF4BD661CAB8A89862DF6603'
        device = await client.find_device(device_name)

        assert device is not None
        assert device.get_alias() == device_name
        assert device.device_id == device_id
        assert device.device_info is not None
        assert device.device_info.device_type == 'IOT.SMARTPLUGSWITCH'
        assert device.device_info.role == 0
        assert device.device_info.fw_ver == '1.2.6 Build 200727 Rel.121701'
        assert device.device_info.app_server_url == 'http://127.0.0.1:8080'
        assert device.device_info.device_region == 'us-east-1'
        assert device.device_info.device_id == device_id
        assert device.device_info.device_name == 'Wi-Fi Smart Plug With Energy Monitoring'
        assert device.device_info.device_hw_ver == '1.0'
        assert device.device_info.alias == device_name
        assert device.device_info.device_mac == '65A4CE143E03'
        assert device.device_info.oem_id == '3580D70F8387F7B530A5020A325EE8CC'
        assert device.device_info.device_model == 'HS110(US)'
        assert device.device_info.hw_id == 'E0CF474A985A06B8A9EE75C1FEBE03C7'
        assert device.device_info.fw_id == '00000000000000000000000000000000'
        assert device.device_info.is_same_region is True
        assert device.device_info.status == 1
        assert device.child_id is None
        # We can cheat a little with knowledge that this is an enum
        assert device.model_type is not None
        assert device.model_type.name == 'HS110'

    @pytest.mark.asyncio
    async def test_finds_hs300_us_device(self, client):
        device_name = 'TP-LINK_Power Strip_9704'
        device_id = '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E'
        device = await client.find_device(device_name)

        assert device is not None
        assert device.get_alias() == device_name
        assert device.device_id == device_id
        assert device.device_info is not None
        assert device.device_info.device_type == 'IOT.SMARTPLUGSWITCH'
        assert device.device_info.role == 0
        assert device.device_info.fw_ver == '1.0.19 Build 200224 Rel.090814'
        assert device.device_info.app_server_url == 'http://127.0.0.1:8080'
        assert device.device_info.device_region == 'us-east-1'
        assert device.device_info.device_id == device_id
        assert device.device_info.device_name == 'Wi-Fi Smart Power Strip'
        assert device.device_info.device_hw_ver == '1.0'
        assert device.device_info.alias == device_name
        assert device.device_info.device_mac == '28A69C74BA90'
        assert device.device_info.oem_id == 'C20341B1E3455640F77F93C8286CD3E3'
        assert device.device_info.device_model == 'HS300(US)'
        assert device.device_info.hw_id == 'F0209F82A6A831CA4AD1CEE3FE574BA2'
        assert device.device_info.fw_id == '00000000000000000000000000000000'
        assert device.device_info.is_same_region is True
        assert device.device_info.status == 1
        assert device.child_id is None
        # We can cheat a little with knowledge that this is an enum
        assert device.model_type is not None
        assert device.model_type.name == 'HS300'

    @pytest.mark.asyncio
    async def test_finds_unknown_us_device(self, client):
        device_name = 'Test Strip'
        device_id = '140BED90F6EF82191649329403A40C66528411D2'
        device = await client.find_device(device_name)

        assert device is not None
        assert device.get_alias() == device_name
        assert device.device_id == device_id
        assert device.device_info is not None
        assert device.device_info.device_type == 'IOT.SMARTBULB'
        assert device.device_info.role == 0
        assert device.device_info.fw_ver == '1.0.8 Build 210121 Rel.084339'
        assert device.device_info.app_server_url == 'http://127.0.0.1:8080'
        assert device.device_info.device_region == 'us-east-1'
        assert device.device_info.device_id == device_id
        assert device.device_info.device_name == 'Kasa Smart Light Strip, Multicolor'
        assert device.device_info.device_hw_ver == '2.0'
        assert device.device_info.alias == device_name
        assert device.device_info.device_mac == '7B2ACF4AE02B'
        assert device.device_info.oem_id == '8BB9A4E25D621BC7163EEF9CDDE2E37C'
        assert device.device_info.device_model == 'KL430(US)'
        assert device.device_info.hw_id == '6E2F6FA0EEE2CC63C8E1CA1C90698437'
        assert device.device_info.fw_id == '00000000000000000000000000000000'
        assert device.device_info.is_same_region is True
        assert device.device_info.status == 1
        assert device.child_id is None
        # We can cheat a little with knowledge that this is an enum
        assert device.model_type is not None
        assert device.model_type.name == 'UNKNOWN'


@pytest.mark.usefixtures('client')
class TestFindDevices(object):

    @pytest.mark.asyncio
    async def test_finds_multiple_devices(self, client):
        devices_like = 'bedroom'
        devices = await client.find_devices(devices_like)

        assert devices is not None
        assert len(devices) == 2


@pytest.mark.usefixtures('client')
class TestAuth(object):

    @pytest.mark.asyncio
    async def test_auth_no_username_or_password(self, client):
        # Should not see an exception raised
        device_manager = await TPLinkDeviceManager(
            username=None,
            password=None,
            prefetch=False,
            cache_devices=False,
            tplink_cloud_api_host=os.environ.get('TPLINK_KASA_API_URL'),
            verbose=False,
            term_id=os.environ.get('TPLINK_KASA_TERM_ID')
        )
        assert device_manager is not None

    @pytest.mark.asyncio
    async def test_auth_no_username(self, client):
        with pytest.raises(ValueError):
            device_manager = await TPLinkDeviceManager(
                username=None,
                password=None,
                prefetch=False,
                cache_devices=False,
                tplink_cloud_api_host=os.environ.get('TPLINK_KASA_API_URL'),
                verbose=False,
                term_id=os.environ.get('TPLINK_KASA_TERM_ID')
            )
            device_manager.login(None, os.environ.get('TPLINK_KASA_PASSWORD'))

    @pytest.mark.asyncio
    async def test_auth_no_password(self, client):
        with pytest.raises(ValueError):
            device_manager = await TPLinkDeviceManager(
                username=None,
                password=None,
                prefetch=False,
                cache_devices=False,
                tplink_cloud_api_host=os.environ.get('TPLINK_KASA_API_URL'),
                verbose=False,
                term_id=os.environ.get('TPLINK_KASA_TERM_ID')
            )
            device_manager.login(os.environ.get('TPLINK_KASA_USERNAME'), None)
