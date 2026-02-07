from tplinkcloud.api_response import TPLinkApiResponse


class TestTPLinkApiResponse:

    def test_successful_response(self):
        resp = TPLinkApiResponse({"error_code": 0, "result": {"token": "abc"}})
        assert resp.successful is True
        assert resp.error_code == 0
        assert resp.result == {"token": "abc"}

    def test_failed_response(self):
        resp = TPLinkApiResponse({"error_code": -20601, "msg": "Bad credentials"})
        assert resp.successful is False
        assert resp.error_code == -20601
        assert resp.msg == "Bad credentials"

    def test_missing_fields(self):
        resp = TPLinkApiResponse({})
        assert resp.successful is False
        assert resp.error_code is None
        assert resp.result is None
        assert resp.msg is None

    def test_mfa_response(self):
        resp = TPLinkApiResponse({
            "error_code": -20677,
            "msg": "MFA required",
            "result": {"mfaType": "verifyCodeLogin"}
        })
        assert resp.successful is False
        assert resp.error_code == -20677
        assert resp.result["mfaType"] == "verifyCodeLogin"
