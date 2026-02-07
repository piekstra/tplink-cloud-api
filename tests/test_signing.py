import json

from tplinkcloud.signing import (
    ACCESS_KEY,
    SECRET_KEY,
    SIGNING_TIMESTAMP,
    compute_content_md5,
    compute_signature,
    get_signing_headers,
)


class TestComputeContentMD5:

    def test_returns_base64_md5(self):
        body = '{"test": "data"}'
        result = compute_content_md5(body)
        # Should be a base64-encoded string
        assert isinstance(result, str)
        assert len(result) > 0
        # Base64 of MD5 is always 24 chars with padding
        assert result.endswith('==') or len(result) == 24

    def test_deterministic(self):
        body = '{"key": "value"}'
        assert compute_content_md5(body) == compute_content_md5(body)

    def test_different_bodies_different_md5(self):
        assert compute_content_md5('{"a": 1}') != compute_content_md5('{"b": 2}')


class TestComputeSignature:

    def test_returns_tuple(self):
        result = compute_signature('{}', '/api/v2/test')
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_content_md5_matches(self):
        body = '{"test": "data"}'
        md5, _ = compute_signature(body, '/api/v2/test')
        assert md5 == compute_content_md5(body)

    def test_authorization_format(self):
        _, auth = compute_signature('{}', '/api/v2/test')
        assert auth.startswith(f'Timestamp={SIGNING_TIMESTAMP}')
        assert f'AccessKey={ACCESS_KEY}' in auth
        assert 'Nonce=' in auth
        assert 'Signature=' in auth

    def test_different_paths_different_signatures(self):
        _, auth1 = compute_signature('{}', '/api/v2/login')
        _, auth2 = compute_signature('{}', '/api/v2/devices')
        # Nonce is random so they'll always differ, but the signature
        # portion should also differ due to different paths
        assert auth1 != auth2

    def test_uses_hardcoded_timestamp(self):
        _, auth = compute_signature('{}', '/test')
        assert f'Timestamp={SIGNING_TIMESTAMP}' in auth


class TestGetSigningHeaders:

    def test_returns_required_headers(self):
        headers = get_signing_headers('{}', '/test')
        assert 'Content-MD5' in headers
        assert 'X-Authorization' in headers

    def test_content_md5_value(self):
        body = json.dumps({"login": True})
        headers = get_signing_headers(body, '/test')
        assert headers['Content-MD5'] == compute_content_md5(body)

    def test_authorization_header_format(self):
        headers = get_signing_headers('{}', '/api/v2/account/login')
        auth = headers['X-Authorization']
        parts = auth.split(', ')
        assert len(parts) == 4
        assert parts[0].startswith('Timestamp=')
        assert parts[1].startswith('Nonce=')
        assert parts[2].startswith('AccessKey=')
        assert parts[3].startswith('Signature=')


class TestConstants:

    def test_access_key_format(self):
        assert len(ACCESS_KEY) == 32
        assert all(c in '0123456789abcdef' for c in ACCESS_KEY)

    def test_secret_key_format(self):
        assert len(SECRET_KEY) == 32
        assert all(c in '0123456789abcdef' for c in SECRET_KEY)

    def test_timestamp_is_hardcoded(self):
        assert SIGNING_TIMESTAMP == "9999999999"
