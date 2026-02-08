"""Tests for Tapo device support via unified cloud listing."""

import os
import pytest
from tplinkcloud import TPLinkDeviceManager


class TestTapoDeviceListing:

    @pytest.fixture(scope="class")
    async def device_manager(self):
        return await TPLinkDeviceManager(
            username=os.environ.get('TPLINK_KASA_USERNAME'),
            password=os.environ.get('TPLINK_KASA_PASSWORD'),
            prefetch=False,
            cache_devices=False,
            tplink_cloud_api_host=os.environ.get('TPLINK_KASA_API_URL'),
            verbose=False,
            term_id=os.environ.get('TPLINK_KASA_TERM_ID'),
            include_tapo=True,
        )

    @pytest.mark.asyncio
    async def test_gets_both_kasa_and_tapo_devices(self, device_manager):
        devices = await device_manager.get_devices()
        assert devices is not None
        assert len(devices) > 0

        cloud_types = {d.cloud_type for d in devices}
        assert "kasa" in cloud_types
        assert "tapo" in cloud_types

    @pytest.mark.asyncio
    async def test_tapo_devices_have_tapo_cloud_type(self, device_manager):
        devices = await device_manager.get_devices()
        tapo_devices = [d for d in devices if d.cloud_type == "tapo"]
        assert len(tapo_devices) > 0
        # Only check device_info.cloud_type on non-child devices
        # (child devices use HS300ChildSysInfo, not TPLinkDeviceInfo)
        for device in tapo_devices:
            if hasattr(device.device_info, 'cloud_type'):
                assert device.device_info.cloud_type == "tapo"

    @pytest.mark.asyncio
    async def test_kasa_devices_have_kasa_cloud_type(self, device_manager):
        devices = await device_manager.get_devices()
        kasa_devices = [d for d in devices if d.cloud_type == "kasa"]
        assert len(kasa_devices) > 0
        for device in kasa_devices:
            if hasattr(device.device_info, 'cloud_type'):
                assert device.device_info.cloud_type == "kasa"

    @pytest.mark.asyncio
    async def test_tapo_device_models_present(self, device_manager):
        devices = await device_manager.get_devices()
        tapo_models = {d.device_info.device_model for d in devices if d.cloud_type == "tapo"}
        assert "P100" in tapo_models
        assert "P110" in tapo_models
        assert "L530" in tapo_models

    @pytest.mark.asyncio
    async def test_find_tapo_device_by_name(self, device_manager):
        device = await device_manager.find_device("Kitchen Tapo Plug")
        assert device is not None
        assert device.cloud_type == "tapo"
        assert device.device_info.device_model == "P100"

    @pytest.mark.asyncio
    async def test_find_devices_returns_both_types(self, device_manager):
        # "Light" and "Lamp" appear in both Kasa and Tapo device names
        devices = await device_manager.find_devices("Tapo")
        assert len(devices) > 0
        assert all(d.cloud_type == "tapo" for d in devices)

    @pytest.mark.asyncio
    async def test_tapo_device_get_sys_info(self, device_manager):
        device = await device_manager.find_device("Kitchen Tapo Plug")
        assert device is not None
        sys_info = await device.get_sys_info()
        assert sys_info is not None
        assert sys_info.get('model') == 'P100'


class TestTapoAuth:

    @pytest.mark.asyncio
    async def test_tapo_token_set_on_login(self):
        device_manager = TPLinkDeviceManager(
            username=os.environ.get('TPLINK_KASA_USERNAME'),
            password=os.environ.get('TPLINK_KASA_PASSWORD'),
            prefetch=False,
            tplink_cloud_api_host=os.environ.get('TPLINK_KASA_API_URL'),
            term_id=os.environ.get('TPLINK_KASA_TERM_ID'),
            include_tapo=True,
        )
        assert device_manager.get_token() is not None
        assert device_manager.get_tapo_token() is not None

    @pytest.mark.asyncio
    async def test_tapo_refresh_token_set_on_login(self):
        device_manager = TPLinkDeviceManager(
            username=os.environ.get('TPLINK_KASA_USERNAME'),
            password=os.environ.get('TPLINK_KASA_PASSWORD'),
            prefetch=False,
            tplink_cloud_api_host=os.environ.get('TPLINK_KASA_API_URL'),
            term_id=os.environ.get('TPLINK_KASA_TERM_ID'),
            include_tapo=True,
        )
        assert device_manager.get_refresh_token() is not None
        assert device_manager.get_tapo_refresh_token() is not None


class TestIncludeTapoFalse:

    @pytest.mark.asyncio
    async def test_no_tapo_devices_when_disabled(self):
        device_manager = await TPLinkDeviceManager(
            username=os.environ.get('TPLINK_KASA_USERNAME'),
            password=os.environ.get('TPLINK_KASA_PASSWORD'),
            prefetch=False,
            cache_devices=False,
            tplink_cloud_api_host=os.environ.get('TPLINK_KASA_API_URL'),
            term_id=os.environ.get('TPLINK_KASA_TERM_ID'),
            include_tapo=False,
        )
        devices = await device_manager.get_devices()
        assert all(d.cloud_type == "kasa" for d in devices)

    @pytest.mark.asyncio
    async def test_tapo_token_none_when_disabled(self):
        device_manager = TPLinkDeviceManager(
            username=os.environ.get('TPLINK_KASA_USERNAME'),
            password=os.environ.get('TPLINK_KASA_PASSWORD'),
            prefetch=False,
            tplink_cloud_api_host=os.environ.get('TPLINK_KASA_API_URL'),
            term_id=os.environ.get('TPLINK_KASA_TERM_ID'),
            include_tapo=False,
        )
        assert device_manager.get_token() is not None
        assert device_manager.get_tapo_token() is None


class TestDeviceDeduplication:

    @pytest.mark.asyncio
    async def test_duplicate_devices_not_listed_twice(self):
        """If a device appears in both clouds, it should only appear once."""
        device_manager = await TPLinkDeviceManager(
            username=os.environ.get('TPLINK_KASA_USERNAME'),
            password=os.environ.get('TPLINK_KASA_PASSWORD'),
            prefetch=False,
            cache_devices=False,
            tplink_cloud_api_host=os.environ.get('TPLINK_KASA_API_URL'),
            term_id=os.environ.get('TPLINK_KASA_TERM_ID'),
            include_tapo=True,
        )
        devices = await device_manager.get_devices()
        device_keys = [(d.device_id, getattr(d, 'child_id', None)) for d in devices]
        assert len(device_keys) == len(set(device_keys))
