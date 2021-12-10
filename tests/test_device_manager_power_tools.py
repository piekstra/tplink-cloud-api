import os
import pytest
from freezegun import freeze_time

from tplinkcloud import TPLinkDeviceManager, TPLinkDeviceManagerPowerTools

@pytest.fixture(scope='module')
async def power_tools():
    client = await TPLinkDeviceManager(
        username=os.environ.get('TPLINK_KASA_USERNAME'),
        password=os.environ.get('TPLINK_KASA_PASSWORD'),
        tplink_cloud_api_host=os.environ.get('TPLINK_KASA_API_URL'),
        verbose=False,
        term_id=os.environ.get('TPLINK_KASA_TERM_ID')
    )
    return TPLinkDeviceManagerPowerTools(
        client
    )

@pytest.mark.usefixtures('power_tools')
class TestDeviceManagerPowerTools(object):

    @pytest.mark.asyncio
    async def test_get_emeter_devices_gets_emeter_devices(self, power_tools):
        emeter_device_list = await power_tools.get_emeter_devices()

        assert emeter_device_list is not None
        # 1 device plus the 6 emeter devices (children) associated with another
        assert len(emeter_device_list) == 7

    @pytest.mark.asyncio
    async def test_get_emeter_devices_gets_emeter_devices_with_substring(self, power_tools):
        devices_like = 'light'
        matching_emeter_devices = await power_tools.get_emeter_devices(devices_like)

        assert matching_emeter_devices is not None
        assert len(matching_emeter_devices) == 1

    @pytest.mark.asyncio
    async def test_get_devices_power_usage_realtime_gets_usage(self, power_tools):
        devices_like = 'plug'
        usage = await power_tools.get_devices_power_usage_realtime(devices_like)

        child_id_iter = iter([
            '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E00',
            '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E01',
            '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E02',
            '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E03',
            '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E04',
            '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E05',
        ])
        
        assert usage is not None
        assert len(usage) == 6
        for device_usage in usage:
            assert device_usage.device_id == '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E'
            assert device_usage.child_id == next(child_id_iter)
            assert device_usage.data is not None
            assert device_usage.data.current_ma > 0
            assert device_usage.data.power_mw > 0
            assert device_usage.data.total_wh > 0
            assert device_usage.data.voltage_mv > 0

    @pytest.mark.asyncio
    @freeze_time("2021-04-09")
    async def test_get_devices_power_usage_day_gets_usage(self, power_tools):        
        devices_like = 'plug'
        usage = await power_tools.get_devices_power_usage_day(devices_like)
        
        child_id_iter = iter([
            '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E00',
            '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E01',
            '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E02',
            '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E03',
            '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E04',
            '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E05',
        ])

        assert usage is not None
        assert len(usage) == 6
        for device_usage in usage:
            assert device_usage.device_id == '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E'
            assert device_usage.child_id == next(child_id_iter)
            assert device_usage.data is not None
            # Should be 30 days worth
            assert len(device_usage.data) == 30
            # For month 03 we expect data for days 11 through 31 inclusive
            # For month 04 we expect data for days 1 through 9 inclusive
            # Hack together an iterator that will return the correct month and day
            month_day_iter = iter([(3,day) for day in range(11,32)]+[(4,day) for day in range(1,10)])
            for data_item in device_usage.data:
                month, day = next(month_day_iter)
                assert data_item.energy_wh > 0
                assert data_item.day == day
                assert data_item.month == month
                assert data_item.year == 2021

    @pytest.mark.asyncio
    @freeze_time("2021-04-09")
    async def test_get_devices_power_usage_month_gets_usage(self, power_tools):
        devices_like = 'plug'
        usage = await power_tools.get_devices_power_usage_month(devices_like)
        
        child_id_iter = iter([
            '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E00',
            '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E01',
            '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E02',
            '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E03',
            '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E04',
            '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E05',
        ])
        
        assert usage is not None
        assert len(usage) == 6
        for device_usage in usage:
            assert device_usage.device_id == '5BFA53B31294DDA5AB4DEBA1B62582E8EC2F789E'
            assert device_usage.child_id == next(child_id_iter)
            assert device_usage.data is not None

            # Should be two months worth
            assert len(device_usage.data) == 2
            month_iter = iter([3, 4])
            for data_item in device_usage.data:
                assert data_item.energy_wh > 0
                assert data_item.month == next(month_iter)
                assert data_item.year == 2021
