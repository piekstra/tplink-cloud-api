"""HMAC-SHA1 request signing for TP-Link Cloud API V2.

The V2 API requires all requests to be signed with HMAC-SHA1.
The signing protocol uses an AccessKey/SecretKey pair that identifies
the client application (not the user).

Signature format:
    sig_string = "{content_md5}\\n{timestamp}\\n{nonce}\\n{url_path}"
    signature = HMAC-SHA1(secret_key, sig_string)

The signature is sent via the X-Authorization header:
    X-Authorization: Timestamp={ts}, Nonce={nonce}, AccessKey={ak}, Signature={sig}
"""

import base64
import hashlib
import hmac
import uuid


# App-level keys from Kasa Android APK (identify the app, not the user)
ACCESS_KEY = "e37525375f8845999bcc56d5e6faa76d"
SECRET_KEY = "314bc6700b3140ca80bc655e527cb062"

# The Kasa app uses a hardcoded timestamp for signing
SIGNING_TIMESTAMP = "9999999999"


def compute_content_md5(body: str) -> str:
    """Compute Base64-encoded MD5 hash of the request body."""
    return base64.b64encode(
        hashlib.md5(body.encode()).digest()
    ).decode()


def compute_signature(body_json: str, url_path: str) -> tuple[str, str]:
    """Compute HMAC-SHA1 signature for a V2 API request.

    Args:
        body_json: The JSON-serialized request body.
        url_path: The URL path (e.g. "/api/v2/account/login"). Must not
                  include query parameters.

    Returns:
        A tuple of (content_md5, x_authorization_header).
    """
    content_md5 = compute_content_md5(body_json)
    nonce = str(uuid.uuid4())

    sig_string = f"{content_md5}\n{SIGNING_TIMESTAMP}\n{nonce}\n{url_path}"
    signature = hmac.new(
        SECRET_KEY.encode(),
        sig_string.encode(),
        hashlib.sha1,
    ).hexdigest()

    authorization = (
        f"Timestamp={SIGNING_TIMESTAMP}, "
        f"Nonce={nonce}, "
        f"AccessKey={ACCESS_KEY}, "
        f"Signature={signature}"
    )

    return content_md5, authorization


def get_signing_headers(body_json: str, url_path: str) -> dict[str, str]:
    """Get the headers required for a signed V2 API request.

    Args:
        body_json: The JSON-serialized request body.
        url_path: The URL path (without query parameters).

    Returns:
        Dict with Content-MD5 and X-Authorization headers.
    """
    content_md5, authorization = compute_signature(body_json, url_path)
    return {
        "Content-MD5": content_md5,
        "X-Authorization": authorization,
    }
