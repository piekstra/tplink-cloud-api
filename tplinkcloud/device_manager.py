import asyncio

from .device_info import TPLinkDeviceInfo
from .device_client import TPLinkDeviceClient
from .client import TPLinkApi
from .exceptions import TPLinkTokenExpiredError

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

DEVICE_MODEL_MAP: dict[str, type[TPLinkDevice]] = {
    'HS100': HS100,
    'HS103': HS103,
    'HS105': HS105,
    'HS110': HS110,
    'HS200': HS200,
    'HS300': HS300,
    'KL420L5': KL420L5,
    'KL430': KL430,
    'KP115': KP115,
    'KP125': KP125,
    'KP200': KP200,
    'KP303': KP303,
    'KP400': KP400,
    'EP40': EP40,
}


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
        include_tapo=True,
    ):
        self._verbose = verbose
        self._cache_devices = cache_devices
        self._cached_devices = None
        self._term_id = term_id
        self._username = username
        self._password = password
        self._mfa_callback = mfa_callback
        self._include_tapo = include_tapo

        # Kasa cloud API (always present)
        self._kasa_api = TPLinkApi(
            tplink_cloud_api_host, verbose=self._verbose,
            term_id=self._term_id, cloud_type="kasa",
        )
        self._kasa_token = None
        self._kasa_refresh_token = None

        # Tapo cloud API (optional, enabled by default)
        self._tapo_api = None
        self._tapo_token = None
        self._tapo_refresh_token = None
        if self._include_tapo:
            self._tapo_api = TPLinkApi(
                tplink_cloud_api_host, verbose=self._verbose,
                term_id=self._term_id, cloud_type="tapo",
            )

        if username and password:
            self._login_all(username, password, mfa_callback=mfa_callback)
        self._prefetch = prefetch

    def _login_all(self, username, password, mfa_callback=None):
        """Login to Kasa cloud and optionally Tapo cloud."""
        # Kasa login
        result = self._kasa_api.login(
            username, password, mfa_callback=mfa_callback
        )
        if result:
            self._kasa_token = result.get('token')
            self._kasa_refresh_token = result.get('refreshToken')

        # Tapo login (separate cloud, same credentials)
        if self._tapo_api:
            try:
                tapo_result = self._tapo_api.login(
                    username, password, mfa_callback=mfa_callback
                )
                if tapo_result:
                    self._tapo_token = tapo_result.get('token')
                    self._tapo_refresh_token = tapo_result.get('refreshToken')
            except Exception:
                if self._verbose:
                    print("Tapo cloud login failed, continuing with Kasa only")

    async def async_init(self):
        # Fetch the devices up front if prefetch and cache them if caching
        if self._prefetch and self._cache_devices and self._kasa_token:
            await self.get_devices()
        return self

    def __await__(self):
        return self.async_init().__await__()

    async def get_devices(self):
        if self._cached_devices:
            return self._cached_devices

        devices = []

        # Get Kasa devices
        kasa_devices = await self._get_cloud_devices(
            self._kasa_api, self._kasa_token, self._kasa_refresh_token,
            "kasa",
        )
        devices.extend(kasa_devices)

        # Get Tapo devices
        if self._tapo_api and self._tapo_token:
            tapo_devices = await self._get_cloud_devices(
                self._tapo_api, self._tapo_token, self._tapo_refresh_token,
                "tapo",
            )
            # Deduplicate: if a device appears in both clouds, keep the
            # Kasa version (it's already in the list)
            kasa_device_ids = {d.device_id for d in devices}
            for device in tapo_devices:
                if device.device_id not in kasa_device_ids:
                    devices.append(device)

        if self._cache_devices:
            self._cached_devices = devices

        return devices

    async def _get_cloud_devices(self, api, token, refresh_token, cloud_type):
        """Get devices from a specific cloud (Kasa or Tapo)."""
        try:
            device_info_list = api.get_device_info_list(token)
        except TPLinkTokenExpiredError:
            if refresh_token:
                result = api.refresh_login(refresh_token)
                if result:
                    if cloud_type == "kasa":
                        self._kasa_token = result.get('token')
                        self._kasa_refresh_token = result.get('refreshToken')
                        token = self._kasa_token
                    else:
                        self._tapo_token = result.get('token')
                        self._tapo_refresh_token = result.get('refreshToken')
                        token = self._tapo_token
                device_info_list = api.get_device_info_list(token)
            else:
                raise

        devices = []
        children_gather_tasks = []
        for device_info in device_info_list:
            device = self._construct_device(device_info, api, token, cloud_type)
            devices.append(device)
            if device.has_children():
                children_gather_tasks.append(device.get_children_async())

        devices_children = await asyncio.gather(*children_gather_tasks)
        for device_children in devices_children:
            for child in device_children:
                child.cloud_type = cloud_type
            devices.extend(device_children)

        return devices

    def _construct_device(self, device_info, api, token, cloud_type):
        tplink_device_info = TPLinkDeviceInfo(device_info, cloud_type=cloud_type)
        client = TPLinkDeviceClient(
            tplink_device_info.app_server_url,
            token,
            verbose=self._verbose,
            term_id=self._term_id,
            access_key=api.access_key,
            secret_key=api.secret_key,
            app_name=api._app_name,
            cloud_type=cloud_type,
        )
        model = tplink_device_info.device_model
        device_cls = next(
            (cls for prefix, cls in DEVICE_MODEL_MAP.items() if model.startswith(prefix)),
            TPLinkDevice,
        )
        device = device_cls(client, tplink_device_info.device_id, tplink_device_info)
        device.cloud_type = cloud_type
        return device

    def login(self, username, password, mfa_callback=None):
        """Login to Kasa cloud. For backward compatibility."""
        result = self._kasa_api.login(
            username, password, mfa_callback=mfa_callback
        )
        if result:
            self._kasa_token = result.get('token')
            self._kasa_refresh_token = result.get('refreshToken')
        return self._kasa_token

    def set_auth_token(self, auth_token):
        self._kasa_token = auth_token

    def get_token(self):
        """Get the current Kasa auth token."""
        return self._kasa_token

    def set_refresh_token(self, refresh_token):
        """Set the Kasa refresh token (e.g. when resuming a session)."""
        self._kasa_refresh_token = refresh_token

    def get_refresh_token(self):
        """Get the current Kasa refresh token."""
        return self._kasa_refresh_token

    def get_tapo_token(self):
        """Get the current Tapo auth token."""
        return self._tapo_token

    def get_tapo_refresh_token(self):
        """Get the current Tapo refresh token."""
        return self._tapo_refresh_token

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
