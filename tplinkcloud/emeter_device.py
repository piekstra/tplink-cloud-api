import asyncio

from .device import TPLinkDevice


class CurrentPower:

    def __init__(self, realtime_data):
        self.voltage_mv = realtime_data.get('voltage_mv')
        self.current_ma = realtime_data.get('current_ma')
        self.power_mw = realtime_data.get('power_mw')
        self.total_wh = realtime_data.get('total_wh')


class DayPowerSummary:

    def __init__(self, day_data):
        self.year = day_data.get('year')
        self.month = day_data.get('month')
        self.day = day_data.get('day')
        self.energy_wh = day_data.get('energy_wh')


class MonthPowerSummary:

    def __init__(self, day_data):
        self.year = day_data.get('year')
        self.month = day_data.get('month')
        self.energy_wh = day_data.get('energy_wh')


class TPLinkEMeterDevice(TPLinkDevice):

    def __init__(self, client, device_id, device_info, child_id=None):
        super().__init__(client, device_id, device_info, child_id)
    
    # This is an override for regular devices
    def has_emeter(self):
        return True

    def get_power_usage_realtime(self):
        return asyncio.run(self.get_power_usage_realtime_async())

    async def get_power_usage_realtime_async(self):
        realtime_data = await self._pass_through_request_async(
            'emeter', 
            'get_realtime', 
            None
        )
        if realtime_data.get('err_code') == 0:
            return CurrentPower(realtime_data)
        return None

    def get_power_usage_day(self, year, month):
        return asyncio.run(self.get_power_usage_day_async(year, month))

    async def get_power_usage_day_async(self, year, month):
        day_response_data = await self._pass_through_request_async(
            'emeter',
            'get_daystat',
            {
                'year': year,
                'month': month
            }
        )
        # If there is no data for the requested month, data will be None
        if day_response_data.get('err_code') == 0:
            return [DayPowerSummary(day_data) for day_data in day_response_data['day_list']]
        return []

    def get_power_usage_month(self, year):
        return asyncio.run(self.get_power_usage_month_async(year))

    async def get_power_usage_month_async(self, year):
        month_response_data = await self._pass_through_request_async(
            'emeter',
            'get_monthstat',
            {
                'year': year
            }
        )
        # If there is no data for the requested year, data will be None
        if month_response_data.get('err_code') == 0:
            return [MonthPowerSummary(month_data) for month_data in month_response_data['month_list']]
        return []
