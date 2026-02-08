"""Integration tests that run against the real TP-Link Cloud API.

These tests are SKIPPED by default. To run them, set the following
environment variables:

    export TPLINK_INTEGRATION_TEST=1
    export TPLINK_KASA_USERNAME=your_email@example.com
    export TPLINK_KASA_PASSWORD=your_password

Then run:

    pytest tests/test_integration.py --verbose

These tests will never run in CI.
"""

import os
import pytest

from tplinkcloud import TPLinkDeviceManager

SKIP_REASON = "Set TPLINK_INTEGRATION_TEST=1 with real credentials to run"
skip_unless_integration = pytest.mark.skipif(
    os.environ.get("TPLINK_INTEGRATION_TEST") != "1",
    reason=SKIP_REASON,
)


@skip_unless_integration
class TestIntegrationAuth:

    def test_login_succeeds(self):
        device_manager = TPLinkDeviceManager(
            username=os.environ["TPLINK_KASA_USERNAME"],
            password=os.environ["TPLINK_KASA_PASSWORD"],
            prefetch=False,
        )
        assert device_manager.get_token() is not None

    def test_login_returns_refresh_token(self):
        device_manager = TPLinkDeviceManager(
            username=os.environ["TPLINK_KASA_USERNAME"],
            password=os.environ["TPLINK_KASA_PASSWORD"],
            prefetch=False,
        )
        assert device_manager.get_refresh_token() is not None


@skip_unless_integration
class TestIntegrationDevices:

    @pytest.fixture(scope="class")
    async def device_manager(self):
        return await TPLinkDeviceManager(
            username=os.environ["TPLINK_KASA_USERNAME"],
            password=os.environ["TPLINK_KASA_PASSWORD"],
            prefetch=False,
            cache_devices=False,
        )

    @pytest.mark.asyncio
    async def test_get_devices_returns_list(self, device_manager):
        devices = await device_manager.get_devices()
        assert devices is not None
        assert isinstance(devices, list)
        assert len(devices) > 0

    @pytest.mark.asyncio
    async def test_devices_have_required_fields(self, device_manager):
        devices = await device_manager.get_devices()
        for device in devices:
            assert device.device_id is not None
            assert device.get_alias() is not None
            assert device.model_type is not None
            assert device.device_info is not None

    @pytest.mark.asyncio
    async def test_get_sys_info(self, device_manager):
        devices = await device_manager.get_devices()
        # Get sys info from the first device that isn't a child
        for device in devices:
            if device.child_id is None:
                sys_info = await device.get_sys_info()
                assert sys_info is not None
                break

    @pytest.mark.asyncio
    async def test_find_device_by_name(self, device_manager):
        devices = await device_manager.get_devices()
        if devices:
            first_alias = devices[0].get_alias()
            found = await device_manager.find_device(first_alias)
            assert found is not None
            assert found.get_alias() == first_alias
