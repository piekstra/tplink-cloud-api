"""HMAC-SHA1 request signing for TP-Link Cloud API V2.

The V2 API requires all requests to be signed with HMAC-SHA1.
The signing protocol uses an AccessKey/SecretKey pair that identifies
the client application (not the user).

Both Kasa and Tapo apps use the same signing algorithm but with
different key pairs.

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
KASA_ACCESS_KEY = "e37525375f8845999bcc56d5e6faa76d"
KASA_SECRET_KEY = "314bc6700b3140ca80bc655e527cb062"

# App-level keys from Tapo Android APK (identify the app, not the user)
TAPO_ACCESS_KEY = "4d11b6b9d5ea4d19a829adbb9714b057"
TAPO_SECRET_KEY = "6ed7d97f3e73467f8a5bab90b577ba4c"

# Default to Kasa keys for backward compatibility
ACCESS_KEY = KASA_ACCESS_KEY
SECRET_KEY = KASA_SECRET_KEY

# Both apps use the same hardcoded timestamp for signing
SIGNING_TIMESTAMP = "9999999999"


def compute_content_md5(body: str) -> str:
    """Compute Base64-encoded MD5 hash of the request body."""
    return base64.b64encode(
        hashlib.md5(body.encode()).digest()
    ).decode()


def compute_signature(
    body_json: str,
    url_path: str,
    access_key: str | None = None,
    secret_key: str | None = None,
) -> tuple[str, str]:
    """Compute HMAC-SHA1 signature for a V2 API request.

    Args:
        body_json: The JSON-serialized request body.
        url_path: The URL path (e.g. "/api/v2/account/login"). Must not
                  include query parameters.
        access_key: Override the default AccessKey (for Tapo support).
        secret_key: Override the default SecretKey (for Tapo support).

    Returns:
        A tuple of (content_md5, x_authorization_header).
    """
    ak = access_key or ACCESS_KEY
    sk = secret_key or SECRET_KEY

    content_md5 = compute_content_md5(body_json)
    nonce = str(uuid.uuid4())

    sig_string = f"{content_md5}\n{SIGNING_TIMESTAMP}\n{nonce}\n{url_path}"
    signature = hmac.new(
        sk.encode(),
        sig_string.encode(),
        hashlib.sha1,
    ).hexdigest()

    authorization = (
        f"Timestamp={SIGNING_TIMESTAMP}, "
        f"Nonce={nonce}, "
        f"AccessKey={ak}, "
        f"Signature={signature}"
    )

    return content_md5, authorization


def get_signing_headers(
    body_json: str,
    url_path: str,
    access_key: str | None = None,
    secret_key: str | None = None,
) -> dict[str, str]:
    """Get the headers required for a signed V2 API request.

    Args:
        body_json: The JSON-serialized request body.
        url_path: The URL path (without query parameters).
        access_key: Override the default AccessKey (for Tapo support).
        secret_key: Override the default SecretKey (for Tapo support).

    Returns:
        Dict with Content-MD5 and X-Authorization headers.
    """
    content_md5, authorization = compute_signature(
        body_json, url_path, access_key, secret_key
    )
    return {
        "Content-MD5": content_md5,
        "X-Authorization": authorization,
    }
