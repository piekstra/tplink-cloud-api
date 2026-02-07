import asyncio

from .device_info import TPLinkDeviceInfo
from .device_client import TPLinkDeviceClient
from .client import TPLinkApi
from .exceptions import TPLinkTokenExpiredError

# Supported devices
from .hs100 import HS100
from .hs103 import HS103
from .hs105 import HS105
from .hs110 import HS110
from .hs200 import HS200
from .hs300 import HS300
from .kl420l5 import KL420L5
from .kl430 import KL430
from .kp115 import KP115
from .kp125 import KP125
from .kp200 import KP200
from .kp303 import KP303
from .kp400 import KP400
from .ep40 import EP40
from .device import TPLinkDevice


class TPLinkDeviceManager:

    def __init__(
        self,
        username=None,
        password=None,
        prefetch=True,
        cache_devices=True,
        tplink_cloud_api_host=None,
        verbose=False,
        term_id=None,
        mfa_callback=None,
    ):
        self._verbose = verbose
        self._cache_devices = cache_devices
        self._cached_devices = None
        self._term_id = term_id
        self._auth_token = None
        self._refresh_token = None
        self._username = username
        self._password = password
        self._mfa_callback = mfa_callback

        self._tplink_api = TPLinkApi(
            tplink_cloud_api_host, verbose=self._verbose, term_id=self._term_id)

        if username and password:
            self.login(username, password, mfa_callback=mfa_callback)
        self._prefetch = prefetch

    async def async_init(self):
        # Fetch the devices up front if prefetch and cache them if caching
        if self._prefetch and self._cache_devices and self._auth_token:
            await self.get_devices()
        return self

    def __await__(self):
        return self.async_init().__await__()

    async def get_devices(self):
        if self._cached_devices:
            return self._cached_devices

        try:
            device_info_list = self._tplink_api.get_device_info_list(
                self._auth_token)
        except TPLinkTokenExpiredError:
            if self._refresh_token:
                self._do_refresh()
                device_info_list = self._tplink_api.get_device_info_list(
                    self._auth_token)
            else:
                raise

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
        model = tplink_device_info.device_model
        if model.startswith('HS100'):
            return HS100(client, tplink_device_info.device_id, tplink_device_info)
        elif model.startswith('HS103'):
            return HS103(client, tplink_device_info.device_id, tplink_device_info)
        elif model.startswith('HS105'):
            return HS105(client, tplink_device_info.device_id, tplink_device_info)
        elif model.startswith('HS110'):
            return HS110(client, tplink_device_info.device_id, tplink_device_info)
        elif model.startswith('HS200'):
            return HS200(client, tplink_device_info.device_id, tplink_device_info)
        elif model.startswith('HS300'):
            return HS300(client, tplink_device_info.device_id, tplink_device_info)
        elif model.startswith('KL420L5'):
            return KL420L5(client, tplink_device_info.device_id, tplink_device_info)
        elif model.startswith('KL430'):
            return KL430(client, tplink_device_info.device_id, tplink_device_info)
        elif model.startswith('KP115'):
            return KP115(client, tplink_device_info.device_id, tplink_device_info)
        elif model.startswith('KP125'):
            return KP125(client, tplink_device_info.device_id, tplink_device_info)
        elif model.startswith('KP200'):
            return KP200(client, tplink_device_info.device_id, tplink_device_info)
        elif model.startswith('KP303'):
            return KP303(client, tplink_device_info.device_id, tplink_device_info)
        elif model.startswith('KP400'):
            return KP400(client, tplink_device_info.device_id, tplink_device_info)
        elif model.startswith('EP40'):
            return EP40(client, tplink_device_info.device_id, tplink_device_info)
        else:
            return TPLinkDevice(client, tplink_device_info.device_id, tplink_device_info)

    def login(self, username, password, mfa_callback=None):
        result = self._tplink_api.login(
            username, password, mfa_callback=mfa_callback
        )
        if result:
            self.set_auth_token(result.get('token'))
            self._refresh_token = result.get('refreshToken')
        return self._auth_token

    def _do_refresh(self):
        """Refresh the auth token using the stored refresh token."""
        result = self._tplink_api.refresh_login(self._refresh_token)
        if result:
            self.set_auth_token(result.get('token'))
            self._refresh_token = result.get('refreshToken')

    def set_auth_token(self, auth_token):
        self._auth_token = auth_token

    def get_token(self):
        """Get the current auth token."""
        return self._auth_token

    def set_refresh_token(self, refresh_token):
        """Set the refresh token (e.g. when resuming a session)."""
        self._refresh_token = refresh_token

    def get_refresh_token(self):
        """Get the current refresh token."""
        return self._refresh_token

    async def find_device(self, device_name):
        devices = await self.get_devices()
        # Just return the first match
        for device in devices:
            if device.get_alias() == device_name:
                return device

        return None

    async def find_devices(self, device_names_like):
        devices = await self.get_devices()
        matching_devices = []
        for device in devices:
            if device_names_like.lower() in device.get_alias().lower():
                matching_devices.append(device)

        return matching_devices
