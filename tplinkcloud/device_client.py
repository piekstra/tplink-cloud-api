import aiohttp
import json
import uuid

from .api_response import TPLinkApiResponse
from .certs import get_ca_cert_path
from .signing import KASA_ACCESS_KEY, KASA_SECRET_KEY, get_signing_headers
import ssl


class TPLinkDeviceClient:
    def __init__(self, host, token, verbose=False, term_id=None,
                 access_key=None, secret_key=None, app_name=None,
                 cloud_type="kasa"):
        self.host = host
        self._verbose = verbose
        self._term_id = term_id or str(uuid.uuid4())
        self._access_key = access_key or KASA_ACCESS_KEY
        self._secret_key = secret_key or KASA_SECRET_KEY
        self._cloud_type = cloud_type

        self._params = {
            "appName": app_name or "Kasa_Android_Mix",
            "appVer": "3.4.451",
            "netType": "wifi",
            "termID": self._term_id,
            "ospf": "Android 14",
            "brand": "TPLINK",
            "locale": "en_US",
            "model": "Pixel",
            "termName": "Pixel",
            "termMeta": "Pixel",
            "token": token,
        }
        self._headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 14; Pixel Build/UP1A)",
            "Content-Type": "application/json;charset=UTF-8",
        }

        # Build SSL context with TP-Link's private CA
        self._ssl_context = ssl.create_default_context(cafile=get_ca_cert_path())

    async def _request_post(self, body, url_path="/"):
        if self._verbose:
            print('POST', self.host + url_path, body)

        body_json = json.dumps(body)

        signing_headers = get_signing_headers(
            body_json, url_path,
            access_key=self._access_key,
            secret_key=self._secret_key,
        )
        headers = {**self._headers, **signing_headers}

        url = self.host if url_path == "/" else f"{self.host}{url_path}"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                data=body_json,
                params=self._params,
                headers=headers,
                ssl=self._ssl_context,
                timeout=aiohttp.ClientTimeout(total=600),
            ) as response:
                if response.status == 200:
                    response_json = await response.json(content_type=None)
                    if self._verbose:
                        print(json.dumps(response_json, indent=2))
                    return TPLinkApiResponse(response_json)
                elif response.content:
                    raise Exception(str(response.status) + ': ' +
                                    response.reason + ': ' + str(response.content))
                else:
                    raise Exception(str(response.status) + ': ' + response.reason)

    async def pass_through_request(self, device_id, request_data):
        if self._cloud_type == "tapo":
            # Tapo uses V2-style passthrough endpoint with flat body
            body = {
                'deviceId': device_id,
                'requestData': json.dumps(request_data),
            }
            response = await self._request_post(
                body, url_path="/api/v2/common/passthrough"
            )
        else:
            # Kasa uses V1-style method/params wrapper on root path
            body = {
                'method': 'passthrough',
                'params': {
                    'deviceId': device_id,
                    'requestData': json.dumps(request_data)
                }
            }
            response = await self._request_post(body)

        if response.successful:
            response_data = response.result.get('responseData')
            # Some devices (e.g., Archer routers) return responseData as a dict
            # while others return it as a JSON string
            if isinstance(response_data, str):
                return json.loads(response_data)
            return response_data

        return None
