import pytest

from tplinkcloud.exceptions import (
    TPLinkAuthError,
    TPLinkCloudError,
    TPLinkDeviceOfflineError,
    TPLinkMFARequiredError,
    TPLinkTokenExpiredError,
)


class TestTPLinkCloudError:

    def test_message(self):
        err = TPLinkCloudError("test error")
        assert str(err) == "test error"

    def test_error_code(self):
        err = TPLinkCloudError("test", error_code=-20104)
        assert err.error_code == -20104

    def test_error_code_default_none(self):
        err = TPLinkCloudError("test")
        assert err.error_code is None

    def test_is_exception(self):
        assert issubclass(TPLinkCloudError, Exception)


class TestTPLinkAuthError:

    def test_inherits_from_cloud_error(self):
        assert issubclass(TPLinkAuthError, TPLinkCloudError)

    def test_catches_as_cloud_error(self):
        with pytest.raises(TPLinkCloudError):
            raise TPLinkAuthError("bad credentials", error_code=-20601)

    def test_error_code(self):
        err = TPLinkAuthError("locked", error_code=-20675)
        assert err.error_code == -20675


class TestTPLinkMFARequiredError:

    def test_inherits_from_cloud_error(self):
        assert issubclass(TPLinkMFARequiredError, TPLinkCloudError)

    def test_mfa_type(self):
        err = TPLinkMFARequiredError(
            "mfa needed", error_code=-20677,
            mfa_type="verifyCodeLogin", email="test@test.com"
        )
        assert err.mfa_type == "verifyCodeLogin"
        assert err.email == "test@test.com"
        assert err.error_code == -20677

    def test_defaults(self):
        err = TPLinkMFARequiredError("mfa needed")
        assert err.mfa_type is None
        assert err.email is None


class TestTPLinkTokenExpiredError:

    def test_inherits_from_cloud_error(self):
        assert issubclass(TPLinkTokenExpiredError, TPLinkCloudError)

    def test_error_code(self):
        err = TPLinkTokenExpiredError("expired", error_code=-20651)
        assert err.error_code == -20651


class TestTPLinkDeviceOfflineError:

    def test_inherits_from_cloud_error(self):
        assert issubclass(TPLinkDeviceOfflineError, TPLinkCloudError)
