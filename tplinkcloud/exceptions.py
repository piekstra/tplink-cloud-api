"""Custom exception classes for the TP-Link Cloud API.

Error codes from the V2 API:
    -20104  Parameter doesn't exist (malformed request)
    -20601  Incorrect email or password
    -20675  Account locked (too many failed attempts)
    -20677  MFA code required
    -20651  Token expired
    -20655  Refresh token expired
"""


class TPLinkCloudError(Exception):
    """Base exception for TP-Link Cloud API errors."""

    def __init__(self, message: str, error_code: int | None = None):
        self.error_code = error_code
        super().__init__(message)


class TPLinkAuthError(TPLinkCloudError):
    """Authentication failed (wrong credentials, account locked, etc.)."""


class TPLinkMFARequiredError(TPLinkCloudError):
    """MFA verification code is required to complete login.

    Attributes:
        mfa_type: The type of MFA (e.g. "verifyCodeLogin").
        email: The email address the code was sent to.
    """

    def __init__(
        self,
        message: str,
        error_code: int | None = None,
        mfa_type: str | None = None,
        email: str | None = None,
    ):
        self.mfa_type = mfa_type
        self.email = email
        super().__init__(message, error_code)


class TPLinkTokenExpiredError(TPLinkCloudError):
    """The auth token or refresh token has expired."""


class TPLinkDeviceOfflineError(TPLinkCloudError):
    """The target device is offline or unreachable."""
