"""Keep credentials out of what the library prints or raises."""

import json

REDACTED = "<redacted>"


def _is_credential_key(key):
    name = key.lower()
    return name == "code" or any(
        word in name for word in ("password", "token", "secret")
    )


def redact(value):
    """Return a copy of a JSON-shaped value with its credentials replaced.

    A flag such as ``refreshTokenNeeded`` stays, since a boolean holds no
    secret and the verbose log is clearer with it.
    """
    if isinstance(value, dict):
        return {
            key: REDACTED
            if isinstance(key, str)
            and _is_credential_key(key)
            and not isinstance(item, bool)
            else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    return value


def redact_body(content):
    """Redact a response body for an error message.

    A body that is not a JSON object or list is dropped, not quoted: it can't
    be searched for credentials.
    """
    try:
        parsed = json.loads(content)
    except (TypeError, ValueError):
        return "<non-JSON body omitted>"
    if not isinstance(parsed, (dict, list)):
        return "<non-JSON body omitted>"
    return json.dumps(redact(parsed))
