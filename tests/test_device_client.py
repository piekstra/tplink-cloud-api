import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from tplinkcloud.device_client import TPLinkDeviceClient


class TestPassThroughRequest:

    @pytest.mark.asyncio
    async def test_pass_through_request_handles_string_response_data(self):
        """Test that string responseData is parsed as JSON"""
        client = TPLinkDeviceClient(
            host='http://test.example.com',
            token='test_token'
        )

        mock_response = MagicMock()
        mock_response.successful = True
        mock_response.result = {
            'responseData': '{"system": {"get_sysinfo": {"relay_state": 1}}}'
        }

        with patch.object(client, '_request_post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await client.pass_through_request(
                'device123',
                {'system': {'get_sysinfo': {}}}
            )

        assert result == {'system': {'get_sysinfo': {'relay_state': 1}}}

    @pytest.mark.asyncio
    async def test_pass_through_request_handles_dict_response_data(self):
        """
        Test that dict responseData is returned as-is.
        Some devices (e.g., Archer routers) return responseData as a dict
        instead of a JSON string. Regression test for issue #65.
        """
        client = TPLinkDeviceClient(
            host='http://test.example.com',
            token='test_token'
        )

        mock_response = MagicMock()
        mock_response.successful = True
        # responseData is already a dict, not a JSON string
        mock_response.result = {
            'responseData': {'system': {'get_sysinfo': {'relay_state': 1}}}
        }

        with patch.object(client, '_request_post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await client.pass_through_request(
                'device123',
                {'system': {'get_sysinfo': {}}}
            )

        assert result == {'system': {'get_sysinfo': {'relay_state': 1}}}

    @pytest.mark.asyncio
    async def test_pass_through_request_returns_none_on_failure(self):
        """Test that None is returned when request fails"""
        client = TPLinkDeviceClient(
            host='http://test.example.com',
            token='test_token'
        )

        mock_response = MagicMock()
        mock_response.successful = False

        with patch.object(client, '_request_post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await client.pass_through_request(
                'device123',
                {'system': {'get_sysinfo': {}}}
            )

        assert result is None
