import requests
import json
import uuid

from .api_response import TPLinkApiResponse


class TPLinkApi:
    def __init__(self, host=None, verbose=False, term_id=None):
        self.host = host if host else 'https://wap.tplinkcloud.com'
        self._verbose = verbose
        self._termId = term_id if term_id else str(uuid.uuid4())
        self._default_params = {
            'appName': 'Kasa_Android',
            'termID': self._termId,
            'appVer': '1.4.4.607',
            'ospf': 'Android+6.0.1',
            'netType': 'wifi',
            'locale': 'es_ES'
        }
        self._headers = {
            'User-Agent':
                'Dalvik/2.1.0 (Linux; U; Android 6.0.1; A0001 Build/M4B30X)',
            'Content-Type': 'application/json'
        }

    def _request_post(self, body, token=None):
        if self._verbose:
            print('POST', self.host, body)

        body_json = json.dumps(body)

        if token:
            params = self._default_params.copy()
            params['token'] = token
        else:
            params = self._default_params

        s = requests.Session()
        response = s.request(
            'POST',
            self.host,
            data=body_json,
            params=params,
            headers=self._headers
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

    # Returns a token if properly authenticated
    def login(self, username, password):
        if not username:
            raise ValueError("Cannot login, username is not set")
        if not password:
            raise ValueError("Cannot login, password not set")
        body = {
            'method': 'login',
            'url': self.host,
            'params': {
                'appType': 'Kasa_Android',
                'cloudUserName': username,
                'cloudPassword': password,
                'terminalUUID': self._termId
            }
        }
        response = self._request_post(body)
        if response.successful:
            return response.result.get('token')

        return None

    def get_device_info_list(self, token):
        body = {
            'method': 'getDeviceList'
        }
        response = self._request_post(body, token)
        if response.successful:
            return response.result.get('deviceList')

        return []
