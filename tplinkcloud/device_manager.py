import asyncio

from .device_info import TPLinkDeviceInfo
from .device_client import TPLinkDeviceClient
from .client import TPLinkApi

# Supported devices
from .hs100 import HS100
from .hs103 import HS103
from .hs105 import HS105
from .hs110 import HS110
from .hs300 import HS300
from .kp115 import KP115
from .kp303 import KP303
from .device import TPLinkDevice


class TPLinkDeviceManager:

    def __init__(
        self,
        username,
        password,
        prefetch=True,
        cache_devices=True,
        tplink_cloud_api_host=None,
        verbose=False,
        term_id=None
    ):
        self._verbose = verbose
        self._cache_devices = cache_devices
        self._cached_devices = None
        self._term_id = term_id

        self._tplink_api = TPLinkApi(
            tplink_cloud_api_host, verbose=self._verbose, term_id=self._term_id)
        # We should only need to get this once
        self._auth_token = self._tplink_api.login(username, password)
        # Fetch the devices up front if prefetch and cache them if caching
        if prefetch and self._cache_devices:
            self.get_devices()

    async def _fetch_devices(self):
        if self._cached_devices:
            return self._cached_devices

        device_info_list = self._tplink_api.get_device_info_list(
            self._auth_token)

        devices = []
        children_gather_tasks = []
        for device_info in device_info_list:
            device = self._construct_device(device_info)
            devices.append(device)
            if device.has_children():
                children_gather_tasks.append(device.get_children_async())
        
        devices_children = await asyncio.gather(*children_gather_tasks)
        for device_children in devices_children:
            devices.extend(device_children)

        if self._cache_devices:
            self._device_info_list = device_info_list
            self._cached_devices = devices

        return devices

    def _construct_device(self, device_info):
        # Construct the TPLinkDeviceInfo here for convenience
        tplink_device_info = TPLinkDeviceInfo(device_info)
        # In case the app_server_url is different, we construct a client each time
        client = TPLinkDeviceClient(
            tplink_device_info.app_server_url,
            self._auth_token,
            verbose=self._verbose,
            term_id=self._term_id
        )
        if tplink_device_info.device_model.startswith('HS100'):
            return HS100(client, tplink_device_info.device_id, tplink_device_info)
        elif tplink_device_info.device_model.startswith('HS103'):
            return HS103(client, tplink_device_info.device_id, tplink_device_info)
        elif tplink_device_info.device_model.startswith('HS105'):
            return HS105(client, tplink_device_info.device_id, tplink_device_info)
        elif tplink_device_info.device_model.startswith('HS110'):
            return HS110(client, tplink_device_info.device_id, tplink_device_info)
        elif tplink_device_info.device_model.startswith('HS300'):
            return HS300(client, tplink_device_info.device_id, tplink_device_info)
        elif tplink_device_info.device_model.startswith('KP115'):
            return KP115(client, tplink_device_info.device_id, tplink_device_info)
        elif tplink_device_info.device_model.startswith('KP303'):
            return KP303(client, tplink_device_info.device_id, tplink_device_info)
        else:
            return TPLinkDevice(client, tplink_device_info.device_id, tplink_device_info)

    def get_devices(self):
        return asyncio.run(self._fetch_devices())

    def find_device(self, device_name):
        devices = self.get_devices()
        # Just return the first match
        for device in devices:
            if device.get_alias() == device_name:
                return device

        return None

    def find_devices(self, device_names_like):
        devices = self.get_devices()
        matching_devices = []
        for device in devices:
            if device_names_like.lower() in device.get_alias().lower():
                matching_devices.append(device)

        return matching_devices
