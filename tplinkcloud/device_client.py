import asyncio
import aiohttp
import json
import uuid

from .api_response import TPLinkApiResponse


class TPLinkDeviceClient:
    def __init__(self, host, token, verbose=False, term_id=None):
        self.host = host
        self._verbose = verbose
        self._termId = term_id if term_id else str(uuid.uuid4())
        self._params = {
            'appName': 'Kasa_Android',
            'termID': self._termId,
            'appVer': '1.4.4.607',
            'ospf': 'Android+6.0.1',
            'netType': 'wifi',
            'locale': 'es_ES',
            'token': token
        }
        self._headers = {
            "cache-control": "no-cache",
            'User-Agent':
                'Dalvik/2.1.0 (Linux; U; Android 6.0.1; A0001 Build/M4B30X)',
            'Content-Type': 'application/json'
        }

    async def _request_post_async(self, body):
        if self._verbose:
            print('POST', self.host, body)

        body_json = json.dumps(body)

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.host,
                data=body_json,
                params=self._params,
                headers=self._headers,
                timeout=600
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
    
    def _request_post(self, body):
        return asyncio.run(self._request_post_async(body))

    async def pass_through_request_async(self, device_id, request_data):
        body = {
            'method': 'passthrough',
            'params': {
                'deviceId': device_id,
                'requestData': json.dumps(request_data)
            }
        }
        response = await self._request_post_async(body)
        if response.successful:
            return json.loads(response.result.get('responseData'))

        return None

    def pass_through_request(self, device_id, request_data):
        return asyncio.run(self.pass_through_request_async(device_id, request_data))
