"""Synchronous HTTP client for TP-Link Cloud API authentication and device listing.

Supports both Kasa and Tapo cloud APIs using the V2 protocol:

Kasa: POST https://n-wap.tplinkcloud.com/api/v2/account/login?appName=Kasa_Android_Mix&...
Tapo: POST https://n-wap.i.tplinkcloud.com/api/v2/account/login?appName=TP-Link_Tapo_Android&...

Both use the same signing algorithm (HMAC-SHA1) but with different key pairs.
"""

import json
import uuid

import requests

from .api_response import TPLinkApiResponse
from .certs import get_ca_cert_path
from .exceptions import (
    TPLinkAuthError,
    TPLinkCloudError,
    TPLinkMFARequiredError,
    TPLinkTokenExpiredError,
)
from .signing import (
    KASA_ACCESS_KEY,
    KASA_SECRET_KEY,
    TAPO_ACCESS_KEY,
    TAPO_SECRET_KEY,
    get_signing_headers,
)

# V2 API error codes
_ERR_MFA_REQUIRED = -20677
_ERR_TOKEN_EXPIRED = -20651
_ERR_REFRESH_TOKEN_EXPIRED = -20655
_ERR_WRONG_CREDENTIALS = -20601
_ERR_ACCOUNT_LOCKED = -20675

# Kasa cloud
KASA_HOST = "https://n-wap.tplinkcloud.com"
KASA_APP_TYPE = "Kasa_Android_Mix"
KASA_APP_NAME = "Kasa_Android_Mix"
KASA_APP_VER = "3.4.451"

# Tapo cloud
TAPO_HOST = "https://n-wap.i.tplinkcloud.com"
TAPO_APP_TYPE = "TP-Link_Tapo_Android"
TAPO_APP_NAME = "TP-Link_Tapo_Android"
TAPO_APP_VER = "3.4.451"

# V2 API paths (shared by both Kasa and Tapo)
_PATH_ACCOUNT_STATUS = "/api/v2/account/getAccountStatusAndUrl"
_PATH_LOGIN = "/api/v2/account/login"
_PATH_REFRESH_TOKEN = "/api/v2/account/refreshToken"
_PATH_MFA_LOGIN = "/api/v2/account/checkMFACodeAndLogin"


class TPLinkApi:
    def __init__(self, host=None, verbose=False, term_id=None,
                 cloud_type="kasa"):
        self._verbose = verbose
        self._term_id = term_id or str(uuid.uuid4())
        self._ca_cert_path = get_ca_cert_path()
        self._cloud_type = cloud_type

        if cloud_type == "tapo":
            self._access_key = TAPO_ACCESS_KEY
            self._secret_key = TAPO_SECRET_KEY
            self._app_type = TAPO_APP_TYPE
            self._app_name = TAPO_APP_NAME
            self._app_ver = TAPO_APP_VER
            default_host = TAPO_HOST
        else:
            self._access_key = KASA_ACCESS_KEY
            self._secret_key = KASA_SECRET_KEY
            self._app_type = KASA_APP_TYPE
            self._app_name = KASA_APP_NAME
            self._app_ver = KASA_APP_VER
            default_host = KASA_HOST

        self.host = host or default_host

        # V2 query parameters (sent on all requests)
        self._query_params = {
            "appName": self._app_name,
            "appVer": self._app_ver,
            "netType": "wifi",
            "termID": self._term_id,
            "ospf": "Android 14",
            "brand": "TPLINK",
            "locale": "en_US",
            "model": "Pixel",
            "termName": "Pixel",
            "termMeta": "Pixel",
        }

        self._headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 14; Pixel Build/UP1A)",
            "Content-Type": "application/json;charset=UTF-8",
        }

    @property
    def cloud_type(self):
        return self._cloud_type

    @property
    def access_key(self):
        return self._access_key

    @property
    def secret_key(self):
        return self._secret_key

    def _request_post_v2(self, base_url, url_path, body, token=None):
        """Make a signed V2 API request.

        Args:
            base_url: The base URL (e.g. "https://n-use1-wap.tplinkcloud.com").
            url_path: The API path (e.g. "/api/v2/account/login").
            body: The request body dict (flat format, no method/params wrapper).
            token: Optional auth token to include in query params.

        Returns:
            TPLinkApiResponse
        """
        url = f"{base_url}{url_path}"
        body_json = json.dumps(body)

        params = self._query_params.copy()
        if token:
            params["token"] = token

        signing_headers = get_signing_headers(
            body_json, url_path,
            access_key=self._access_key,
            secret_key=self._secret_key,
        )
        headers = {**self._headers, **signing_headers}

        if self._verbose:
            print(f"POST {url}")
            print(f"Body: {body_json}")

        response = requests.post(
            url,
            data=body_json,
            params=params,
            headers=headers,
            verify=self._ca_cert_path,
            timeout=15,
        )

        if response.status_code == 200:
            response_json = response.json()
            if self._verbose:
                print(json.dumps(response_json, indent=2))
            return TPLinkApiResponse(response_json)

        if response.content:
            raise TPLinkCloudError(
                f"{response.status_code}: {response.reason}: {response.content!r}"
            )
        raise TPLinkCloudError(f"{response.status_code}: {response.reason}")

    def _request_post_v1(self, body, token=None):
        """Make a V1-style request (method/params wrapper) with V2 signing.

        Kasa device operations use the V1 JSON format on the root path,
        but with V2 signing headers and query parameters.
        """
        url_path = "/"
        body_json = json.dumps(body)

        params = self._query_params.copy()
        if token:
            params["token"] = token

        signing_headers = get_signing_headers(
            body_json, url_path,
            access_key=self._access_key,
            secret_key=self._secret_key,
        )
        headers = {**self._headers, **signing_headers}

        if self._verbose:
            print(f"POST {self.host}/")
            print(f"Body: {body_json}")

        response = requests.post(
            self.host,
            data=body_json,
            params=params,
            headers=headers,
            verify=self._ca_cert_path,
            timeout=15,
        )

        if response.status_code == 200:
            response_json = response.json()
            if self._verbose:
                print(json.dumps(response_json, indent=2))
            return TPLinkApiResponse(response_json)

        if response.content:
            raise TPLinkCloudError(
                f"{response.status_code}: {response.reason}: {response.content!r}"
            )
        raise TPLinkCloudError(f"{response.status_code}: {response.reason}")

    def _get_regional_url(self, username):
        """Discover the regional API server URL for the given account.

        Returns:
            The regional appServerUrl string.
        """
        body = {
            "appType": self._app_type,
            "cloudUserName": username,
        }
        response = self._request_post_v2(
            self.host, _PATH_ACCOUNT_STATUS, body
        )
        if response.successful:
            return response.result.get("appServerUrl", self.host)

        return self.host

    def login(self, username, password, mfa_callback=None):
        """Authenticate with the TP-Link Cloud V2 API.

        Flow:
            1. getAccountStatusAndUrl -> regional URL
            2. login on regional URL -> token (or MFA challenge)
            3. If MFA required and callback provided, handle MFA

        Args:
            username: TP-Link / Kasa account email.
            password: Account password.
            mfa_callback: Optional callable(mfa_type, email) -> str that returns
                         the MFA verification code. If MFA is required and no
                         callback is provided, raises TPLinkMFARequiredError.

        Returns:
            Dict with 'token' and optionally 'refreshToken'.

        Raises:
            TPLinkAuthError: Wrong credentials or account locked.
            TPLinkMFARequiredError: MFA required but no callback provided.
        """
        if not username:
            raise ValueError("Cannot login, username is not set")
        if not password:
            raise ValueError("Cannot login, password not set")

        # Step 1: Discover regional URL
        regional_url = self._get_regional_url(username)
        self.host = regional_url

        # Step 2: Login
        login_body = {
            "appType": self._app_type,
            "appVersion": self._app_ver,
            "cloudPassword": password,
            "cloudUserName": username,
            "platform": "Android",
            "refreshTokenNeeded": True,
            "supportBindAccount": False,
            "terminalUUID": self._term_id,
            "terminalName": "Pixel",
            "terminalMeta": "Pixel",
        }

        response = self._request_post_v2(
            regional_url, _PATH_LOGIN, login_body
        )

        error_code = response.error_code
        if error_code == 0:
            return response.result

        # Handle specific error codes
        if error_code == _ERR_MFA_REQUIRED:
            if mfa_callback is None:
                raise TPLinkMFARequiredError(
                    "MFA verification required. Provide an mfa_callback.",
                    error_code=error_code,
                    mfa_type=response.result.get("mfaType") if response.result else None,
                    email=username,
                )
            # Get MFA code from callback and verify
            mfa_type = response.result.get("mfaType", "verifyCodeLogin") if response.result else "verifyCodeLogin"
            mfa_code = mfa_callback(mfa_type, username)
            return self._verify_mfa(regional_url, username, password, mfa_code)

        if error_code in (_ERR_WRONG_CREDENTIALS, _ERR_ACCOUNT_LOCKED):
            raise TPLinkAuthError(
                response.msg or "Authentication failed",
                error_code=error_code,
            )

        raise TPLinkCloudError(
            response.msg or f"Login failed with error code {error_code}",
            error_code=error_code,
        )

    def _verify_mfa(self, regional_url, username, password, mfa_code):
        """Complete MFA verification.

        Returns:
            Dict with 'token' and optionally 'refreshToken'.
        """
        body = {
            "appType": self._app_type,
            "cloudPassword": password,
            "cloudUserName": username,
            "code": mfa_code,
            "terminalUUID": self._term_id,
        }
        response = self._request_post_v2(
            regional_url, _PATH_MFA_LOGIN, body
        )
        if response.successful:
            return response.result

        raise TPLinkAuthError(
            response.msg or "MFA verification failed",
            error_code=response.error_code,
        )

    def refresh_login(self, refresh_token):
        """Refresh an expired auth token using a refresh token.

        Args:
            refresh_token: The refresh token from a previous login.

        Returns:
            Dict with new 'token' and 'refreshToken'.

        Raises:
            TPLinkTokenExpiredError: If the refresh token itself has expired.
        """
        body = {
            "appType": self._app_type,
            "refreshToken": refresh_token,
            "terminalUUID": self._term_id,
        }
        response = self._request_post_v2(
            self.host, _PATH_REFRESH_TOKEN, body
        )
        if response.successful:
            return response.result

        if response.error_code == _ERR_REFRESH_TOKEN_EXPIRED:
            raise TPLinkTokenExpiredError(
                "Refresh token has expired. Full re-login required.",
                error_code=response.error_code,
            )

        raise TPLinkCloudError(
            response.msg or f"Token refresh failed with error code {response.error_code}",
            error_code=response.error_code,
        )

    def get_device_info_list(self, token):
        """Get the list of devices registered to the account.

        Uses V1-style request format with V2 signing.
        """
        body = {
            "method": "getDeviceList",
        }
        response = self._request_post_v1(body, token)
        if response.successful:
            return response.result.get("deviceList", [])

        if response.error_code == _ERR_TOKEN_EXPIRED:
            raise TPLinkTokenExpiredError(
                "Auth token expired",
                error_code=response.error_code,
            )

        return []
