import json

import aiohttp
import pytest
import requests
from multidict import CIMultiDict, CIMultiDictProxy
from yarl import URL

from tplinkcloud.client import TPLinkApi
from tplinkcloud.device_client import TPLinkDeviceClient
from tplinkcloud.exceptions import TPLinkCloudError
from tplinkcloud.redaction import REDACTED, redact, redact_body

PASSWORD = "dummy-password"
TOKEN = "dummy-token"
REFRESH_TOKEN = "dummy-refresh-token"
MFA_CODE = "000000"


class FakeResponse:

    def __init__(self, status_code, payload, reason="OK"):
        self.status_code = status_code
        self.reason = reason
        self.content = json.dumps(payload).encode()
        self._payload = payload

    def json(self):
        return self._payload


def fake_post(response):
    return lambda *args, **kwargs: response


@pytest.fixture
def verbose_client():
    return TPLinkApi(host="https://example.invalid", verbose=True)


def login_reply():
    return FakeResponse(200, {
        "error_code": 0,
        "result": {
            "appServerUrl": "https://example.invalid",
            "token": TOKEN,
            "refreshToken": REFRESH_TOKEN,
        },
    })


class TestRedact:

    def test_replaces_credentials_at_any_depth(self):
        body = {
            "cloudPassword": PASSWORD,
            "nested": {"token": TOKEN, "list": [{"refreshToken": REFRESH_TOKEN}]},
            "code": MFA_CODE,
        }
        assert redact(body) == {
            "cloudPassword": REDACTED,
            "nested": {"token": REDACTED, "list": [{"refreshToken": REDACTED}]},
            "code": REDACTED,
        }

    def test_keeps_what_is_not_a_credential(self):
        body = {"error_code": 0, "refreshTokenNeeded": True, "appType": "x"}
        assert redact(body) == body

    def test_does_not_change_the_body_it_was_given(self):
        body = {"cloudPassword": PASSWORD}
        redact(body)
        assert body == {"cloudPassword": PASSWORD}

    def test_a_response_body_is_redacted_or_dropped(self):
        assert TOKEN not in redact_body(json.dumps({"token": TOKEN}).encode())
        assert TOKEN not in redact_body(f"token={TOKEN}".encode())
        assert TOKEN not in redact_body(json.dumps(TOKEN).encode())


class TestVerboseOutput:

    def test_login_prints_no_credential(self, verbose_client, monkeypatch, capsys):
        monkeypatch.setattr(requests, "post", fake_post(login_reply()))
        result = verbose_client.login("user@example.invalid", PASSWORD)
        printed = capsys.readouterr().out
        assert result["token"] == TOKEN
        assert "cloudPassword" in printed
        for secret in (PASSWORD, TOKEN, REFRESH_TOKEN):
            assert secret not in printed

    def test_mfa_verification_prints_no_credential(
        self, verbose_client, monkeypatch, capsys
    ):
        monkeypatch.setattr(requests, "post", fake_post(login_reply()))
        verbose_client._verify_mfa(
            "https://example.invalid", "user@example.invalid", PASSWORD, MFA_CODE
        )
        printed = capsys.readouterr().out
        for secret in (PASSWORD, MFA_CODE, TOKEN, REFRESH_TOKEN):
            assert secret not in printed

    def test_refresh_prints_no_credential(self, verbose_client, monkeypatch, capsys):
        monkeypatch.setattr(requests, "post", fake_post(login_reply()))
        verbose_client.refresh_login(REFRESH_TOKEN)
        printed = capsys.readouterr().out
        for secret in (TOKEN, REFRESH_TOKEN):
            assert secret not in printed


class TestErrors:

    def test_a_failed_request_does_not_carry_the_token(
        self, verbose_client, monkeypatch
    ):
        def refuse(url, params=None, **kwargs):
            raise requests.ConnectionError(f"Max retries exceeded: {url}?token={params['token']}")

        monkeypatch.setattr(requests, "post", refuse)
        with pytest.raises(requests.ConnectionError) as caught:
            verbose_client._request_post_v1({"method": "getDeviceList"}, TOKEN)
        assert TOKEN not in str(caught.value)
        assert caught.value.__cause__ is None
        assert caught.value.__suppress_context__
        assert caught.value.request is None

    def test_an_error_status_does_not_quote_a_credential(
        self, verbose_client, monkeypatch
    ):
        reply = FakeResponse(500, {"token": TOKEN}, reason="Server Error")
        monkeypatch.setattr(requests, "post", fake_post(reply))
        with pytest.raises(TPLinkCloudError) as caught:
            verbose_client._request_post_v1({"method": "getDeviceList"}, TOKEN)
        assert TOKEN not in str(caught.value)
        assert "500" in str(caught.value)


class FakeDeviceResponse:

    def __init__(self, status, reason, body):
        self.status = status
        self.reason = reason
        self._body = body

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def read(self):
        return self._body


def session_replying(response):
    class Session:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *exc):
            return False

        def post(self, *args, **kwargs):
            return response

    return Session


def session_raising(error):
    class Failing:
        async def __aenter__(self):
            raise error

        async def __aexit__(self, *exc):
            return False

    return session_replying(Failing())


@pytest.fixture
def device_client():
    return TPLinkDeviceClient("https://example.invalid", TOKEN)


class TestDeviceClientErrors:

    @pytest.mark.asyncio
    async def test_a_redirect_failure_does_not_carry_the_token(
        self, device_client, monkeypatch
    ):
        url = URL(f"https://example.invalid/?token={TOKEN}")
        info = aiohttp.RequestInfo(
            url, "POST", CIMultiDictProxy(CIMultiDict()), url
        )
        error = aiohttp.TooManyRedirects(info, ())
        assert TOKEN in str(error)
        monkeypatch.setattr(aiohttp, "ClientSession", session_raising(error))
        with pytest.raises(TPLinkCloudError) as caught:
            await device_client._request_post({"method": "passthrough"})
        assert TOKEN not in str(caught.value)
        assert caught.value.__suppress_context__

    @pytest.mark.asyncio
    async def test_a_connection_failure_keeps_its_type(
        self, device_client, monkeypatch
    ):
        error = aiohttp.ServerDisconnectedError()
        monkeypatch.setattr(aiohttp, "ClientSession", session_raising(error))
        with pytest.raises(aiohttp.ServerDisconnectedError):
            await device_client._request_post({"method": "passthrough"})

    @pytest.mark.asyncio
    async def test_an_error_status_does_not_quote_a_credential(
        self, device_client, monkeypatch
    ):
        body = json.dumps({"token": TOKEN, "msg": "nope"}).encode()
        reply = FakeDeviceResponse(500, "Server Error", body)
        monkeypatch.setattr(aiohttp, "ClientSession", session_replying(reply))
        with pytest.raises(TPLinkCloudError) as caught:
            await device_client._request_post({"method": "passthrough"})
        assert TOKEN not in str(caught.value)
        assert "500" in str(caught.value)
        assert "nope" in str(caught.value)
