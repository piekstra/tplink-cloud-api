import asyncio
from datetime import datetime


class DevicePowerUsage:

    def __init__(self, device_id, child_id, name, data):
        self.device_id = device_id
        # This is only set if the device is a child device
        if child_id:
            self.child_id = child_id
        self.name = name
        self.data = data

# This builds upon the TPLinkDeviceManager, adding functionality specifically 
# pertaining to emeter devices. The main benefit of this toolset is that requests 
# are managed asynchronously across all matching devices, so for a large number of
# devices, getting power data will happen very quickly.
class TPLinkDeviceManagerPowerTools:

    def __init__(
        self,
        device_manager
    ):
        self._device_manager = device_manager
    
    async def get_emeter_devices(self, devices_like=None):
        if devices_like:
            devices = await self._device_manager.find_devices(devices_like)
        else:
            devices = await self._device_manager.get_devices()
        emeter_devices = [device for device in devices if device.has_emeter()]
        return emeter_devices

    async def get_devices_power_usage_realtime(self, devices_like):
        devices = await self.get_emeter_devices(devices_like)
        return await self._get_power_usage_realtime(devices)

    async def get_devices_power_usage_day(self, devices_like):
        devices = await self.get_emeter_devices(devices_like)
        return await self._get_power_usage_day(devices)

    async def get_devices_power_usage_month(self, devices_like):
        devices = await self.get_emeter_devices(devices_like)
        return await self._get_power_usage_month(devices)

    async def _get_device_power_usage_realtime(self, device):
        usage = await device.get_power_usage_realtime()

        return DevicePowerUsage(
            device.device_id,
            device.child_id, # this could be None
            device.get_alias(),
            usage
        )

    async def _get_power_usage_realtime(self, devices):
        device_usage_requests = []
        for device in devices:
            device_usage_requests.append(self._get_device_power_usage_realtime(
                device
            ))

        device_usage = await asyncio.gather(*device_usage_requests)
        return device_usage

    async def _get_device_power_usage_day(self, device, today, previous_month, previous_months_year):
        usage = await device.get_power_usage_day(today.year, today.month)
        previous_month_usage = await device.get_power_usage_day(previous_months_year, previous_month)
        if previous_month_usage:
            usage.extend(previous_month_usage)
        usage.sort(key=lambda x: datetime(year=x.year, month=x.month, day=x.day))

        return DevicePowerUsage(
            device.device_id,
            device.child_id, # this could be None
            device.get_alias(),
            usage
        )

    async def _get_power_usage_day(self, devices):
        today = datetime.today()
        # Data requested by month needs to account for the past month
        if today.month > 1:
            previous_month = today.month - 1
            previous_months_year = today.year
        else:
            previous_month = 12
            previous_months_year = today.year - 1

        device_usage_requests = []
        for device in devices:
            device_usage_requests.append(self._get_device_power_usage_day(
                device,
                today,
                previous_month,
                previous_months_year
            ))

        device_usage = await asyncio.gather(*device_usage_requests)
        return device_usage

    async def _get_device_power_usage_month(self, device, today):
        usage = await device.get_power_usage_month(today.year)
        previous_year_usage = await device.get_power_usage_month(today.year - 1)
        if previous_year_usage:
            usage.extend(previous_year_usage)
        # Given there is no actual day data, just use the same value for each
        usage.sort(key=lambda x: datetime(year=x.year, month=x.month, day=1))

        return DevicePowerUsage(
            device.device_id,
            device.child_id, # this could be None
            device.get_alias(),
            usage
        )

    async def _get_power_usage_month(self, devices):
        today = datetime.today()
        device_usage_requests = []
        for device in devices:
            device_usage_requests.append(self._get_device_power_usage_month(
                device, 
                today
            ))

        device_usage = await asyncio.gather(*device_usage_requests)
        return device_usage
