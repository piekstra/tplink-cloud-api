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
        verbose=True,
        term_id=os.environ.get('TPLINK_KASA_TERM_ID')
    )


@pytest.mark.usefixtures('client')
class TestTPLinkDevice(object):

    @pytest.mark.asyncio
    async def test_get_net_info_gets_net_info(self, client):
        device_name = 'Left Lamp'
        device = await client.find_device(device_name)
        net_info = await device.get_net_info()

        assert net_info is not None
        assert net_info.ssid == "My WiFi Network"
        assert net_info.key_type == 3
        assert net_info.rssi == -39
        assert net_info.err_code == 0

    @pytest.mark.asyncio
    async def test_get_time_gets_time(self, client):
        device_name = 'Left Lamp'
        device = await client.find_device(device_name)
        time = await device.get_time()

        assert time is not None
        assert time.year == 2021
        assert time.month == 3
        assert time.mday == 22
        assert time.hour == 12
        assert time.min == 55
        assert time.sec == 41
        assert time.err_code == 0

    @pytest.mark.asyncio
    async def test_get_timezone_gets_timezone(self, client):
        device_name = 'Left Lamp'
        device = await client.find_device(device_name)
        timezone = await device.get_timezone()

        assert timezone is not None
        assert timezone.index == 6
        assert timezone.err_code == 0


@pytest.mark.usefixtures('client')
class TestTPLinkDeviceSchedule(object):

    @pytest.mark.asyncio
    async def test_get_schedule_rules_gets_schedule_rules(self, client):
        device_name = 'Left Lamp'
        device = await client.find_device(device_name)
        schedule = await device.get_schedule_rules()

        assert schedule is not None
        # Unsure what this field is for
        assert schedule.version is None
        assert schedule.enable == 1
        assert schedule.err_code == 0
        assert schedule.rules is not None
        assert len(schedule.rules) == 4

        # Time-based schedule rule
        assert schedule.rules[0].id == '7B0F854D3C0384E48EF88E0187BD8F34'
        assert schedule.rules[0].name == 'Schedule Rule'

        assert schedule.rules[0].enable == 1
        assert schedule.rules[0].enabled

        assert schedule.rules[0].wday == [1,0,1,1,0,1,1]
        assert schedule.rules[0].sunday_enabled
        assert not schedule.rules[0].monday_enabled
        assert schedule.rules[0].tuesday_enabled
        assert schedule.rules[0].wednesday_enabled
        assert not schedule.rules[0].thursday_enabled
        assert schedule.rules[0].friday_enabled
        assert schedule.rules[0].saturday_enabled

        assert schedule.rules[0].stime_opt == 0
        assert schedule.rules[0].start_type.name == 'Time'

        assert schedule.rules[0].soffset is None
        assert schedule.rules[0].smin == 705
        assert schedule.rules[0].hour == 11
        assert schedule.rules[0].minute == 45

        assert schedule.rules[0].sact == 1
        assert schedule.rules[0].turn_on
        assert not schedule.rules[0].turn_off

        assert schedule.rules[0].etime_opt == -1
        assert schedule.rules[0].eoffset is None
        assert schedule.rules[0].emin == 0
        assert schedule.rules[0].eact == -1

        assert schedule.rules[0].repeat == 1
        assert schedule.rules[0].repeated

        assert schedule.rules[0].year == 0
        assert schedule.rules[0].month == 0
        assert schedule.rules[0].day == 0

        # Sunrise schedule rule
        assert schedule.rules[1].id == 'E6F1B23B134009FDDEA89E59F46E8708'
        assert schedule.rules[1].name == 'Schedule Rule'

        assert schedule.rules[1].enable == 1
        assert schedule.rules[1].enabled

        assert schedule.rules[1].wday == [1,1,1,1,1,1,1]
        assert schedule.rules[1].sunday_enabled
        assert schedule.rules[1].monday_enabled
        assert schedule.rules[1].tuesday_enabled
        assert schedule.rules[1].wednesday_enabled
        assert schedule.rules[1].thursday_enabled
        assert schedule.rules[1].friday_enabled
        assert schedule.rules[1].saturday_enabled

        assert schedule.rules[1].stime_opt == 1
        assert schedule.rules[1].start_type.name == 'Sunrise'

        assert schedule.rules[1].soffset is None
        assert schedule.rules[1].smin == 389
        assert schedule.rules[1].hour == 6
        assert schedule.rules[1].minute == 29

        assert schedule.rules[1].sact == 1
        assert schedule.rules[1].turn_on
        assert not schedule.rules[1].turn_off

        assert schedule.rules[1].etime_opt == -1
        assert schedule.rules[1].eoffset is None
        assert schedule.rules[1].emin == 0
        assert schedule.rules[1].eact == -1

        assert schedule.rules[1].repeat == 1
        assert schedule.rules[1].repeated

        assert schedule.rules[1].year == 0
        assert schedule.rules[1].month == 0
        assert schedule.rules[1].day == 0

        # Sunset schedule rule
        assert schedule.rules[2].id == '558AD8513338E5A4154CFC595BA72B83'
        assert schedule.rules[2].name == 'Schedule Rule'

        assert schedule.rules[2].enable == 1
        assert schedule.rules[2].enabled

        assert schedule.rules[2].wday == [0,1,1,1,1,1,0]
        assert not schedule.rules[2].sunday_enabled
        assert schedule.rules[2].monday_enabled
        assert schedule.rules[2].tuesday_enabled
        assert schedule.rules[2].wednesday_enabled
        assert schedule.rules[2].thursday_enabled
        assert schedule.rules[2].friday_enabled
        assert not schedule.rules[2].saturday_enabled

        assert schedule.rules[2].stime_opt == 2
        assert schedule.rules[2].start_type.name == 'Sunset'

        assert schedule.rules[2].soffset is None
        assert schedule.rules[2].smin == 1195
        assert schedule.rules[2].hour == 19
        assert schedule.rules[2].minute == 55

        assert schedule.rules[2].sact == 0
        assert not schedule.rules[2].turn_on
        assert schedule.rules[2].turn_off

        assert schedule.rules[2].etime_opt == -1
        assert schedule.rules[2].eoffset is None
        assert schedule.rules[2].emin == 0
        assert schedule.rules[2].eact == -1

        assert schedule.rules[2].repeat == 1
        assert schedule.rules[2].repeated

        assert schedule.rules[2].year == 0
        assert schedule.rules[2].month == 0
        assert schedule.rules[2].day == 0

        # One-off Time-based schedule rule
        assert schedule.rules[3].id == 'FF24375EB7DD5F3D9AEFE22EAA11E436'
        assert schedule.rules[3].name == 'Schedule Rule'

        assert schedule.rules[3].enable == 0
        assert not schedule.rules[3].enabled

        assert schedule.rules[3].wday == [1,0,0,0,0,0,0]
        assert schedule.rules[3].sunday_enabled
        assert not schedule.rules[3].monday_enabled
        assert not schedule.rules[3].tuesday_enabled
        assert not schedule.rules[3].wednesday_enabled
        assert not schedule.rules[3].thursday_enabled
        assert not schedule.rules[3].friday_enabled
        assert not schedule.rules[3].saturday_enabled

        assert schedule.rules[3].stime_opt == 0
        assert schedule.rules[3].start_type.name == 'Time'

        assert schedule.rules[3].soffset is None
        assert schedule.rules[3].smin == 719
        assert schedule.rules[3].hour == 11
        assert schedule.rules[3].minute == 59

        assert schedule.rules[3].sact == 0
        assert not schedule.rules[3].turn_on
        assert schedule.rules[3].turn_off

        assert schedule.rules[3].etime_opt == -1
        assert schedule.rules[3].eoffset is None
        assert schedule.rules[3].emin == 0
        assert schedule.rules[3].eact == -1

        assert schedule.rules[3].repeat == 0
        assert not schedule.rules[3].repeated

        assert schedule.rules[3].year == 2021
        assert schedule.rules[3].month == 4
        assert schedule.rules[3].day == 11