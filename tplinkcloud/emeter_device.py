import asyncio

from .device import TPLinkDevice
from .device_type import TPLinkDeviceType


class CurrentPower:

    def __init__(self, realtime_data):
        # The HS110 does not have the unit type suffixes, and others
        # also may not but have yet to be identified. We attempt to
        # normalize the results by trying both possible keys
        self.voltage_mv = realtime_data.get('voltage_mv')
        if self.voltage_mv is None:
            self.voltage_mv = realtime_data.get('voltage')

        self.current_ma = realtime_data.get('current_ma')
        if self.current_ma is None:
            self.current_ma = realtime_data.get('current')

        self.power_mw = realtime_data.get('power_mw')
        if self.power_mw is None:
            self.power_mw = realtime_data.get('power')

        self.total_wh = realtime_data.get('total_wh')
        if self.total_wh is None:
            self.total_wh = realtime_data.get('total')


class DayPowerSummary:

    def __init__(self, day_data):
        self.year = day_data.get('year')
        self.month = day_data.get('month')
        self.day = day_data.get('day')
        # The HS110 does not have the unit type suffixes, and others
        # also may not but have yet to be identified. We attempt to
        # normalize the results by trying both possible keys
        self.energy_wh = day_data.get('energy_wh')
        if self.energy_wh is None:
            self.energy_wh = day_data.get('energy')


class MonthPowerSummary:

    def __init__(self, day_data):
        self.year = day_data.get('year')
        self.month = day_data.get('month')
        # The HS110 does not have the unit type suffixes, and others
        # also may not but have yet to be identified. We attempt to
        # normalize the results by trying both possible keys
        self.energy_wh = day_data.get('energy_wh')
        if self.energy_wh is None:
            self.energy_wh = day_data.get('energy')


class TPLinkEMeterDevice(TPLinkDevice):

    def __init__(self, client, device_id, device_info, child_id=None):
        super().__init__(client, device_id, device_info, child_id)

    # This is an override for regular devices
    def has_emeter(self):
        return True

    async def get_power_usage_realtime(self):
        realtime_data = await self._pass_through_request(
            'emeter',
            'get_realtime',
            None
        )
        if realtime_data is not None and realtime_data.get('err_code') == 0:
            return CurrentPower(realtime_data)
        return None

    async def get_power_usage_day(self, year, month):
        day_response_data = await self._pass_through_request(
            'emeter',
            'get_daystat',
            {
                'year': year,
                'month': month
            }
        )
        # If there is no data for the requested month, data will be None
        if day_response_data and day_response_data.get('err_code') == 0:
            return [DayPowerSummary(day_data) for day_data in day_response_data['day_list']]
        return []

    async def get_power_usage_month(self, year):
        month_response_data = await self._pass_through_request(
            'emeter',
            'get_monthstat',
            {
                'year': year
            }
        )
        # If there is no data for the requested year, data will be None
        if month_response_data and month_response_data.get('err_code') == 0:
            return [MonthPowerSummary(month_data) for month_data in month_response_data['month_list']]
        return []
