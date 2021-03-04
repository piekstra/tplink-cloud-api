import requests
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

    def _request_post(self, body):
        if self._verbose:
            print('POST', self.host, body)

        body_json = json.dumps(body)

        s = requests.Session()
        response = s.request(
            'POST',
            self.host,
            data=body_json,
            params=self._params,
            headers=self._headers,
            timeout=600
        )

        if response.status_code == 200:
            response_json = response.json()
            if self._verbose:
                print(json.dumps(response_json, indent=2))
            return TPLinkApiResponse(response_json)
        elif response.content:
            raise Exception(str(response.status_code) + ': ' +
                            response.reason + ': ' + str(response.content))
        else:
            raise Exception(str(response.status_code) + ': ' + response.reason)

    def pass_through_request(self, device_id, request_data):
        body = {
            'method': 'passthrough',
            'params': {
                'deviceId': device_id,
                'requestData': json.dumps(request_data)
            }
        }
        response = self._request_post(body)
        if response.successful:
            return json.loads(response.result.get('responseData'))

        return None
