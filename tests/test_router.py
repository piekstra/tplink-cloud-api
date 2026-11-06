"""Tests for the Router device class and supporting metadata."""
import pytest

from tplinkcloud.device_info import TPLinkDeviceInfo
from tplinkcloud.device_type import TPLinkDeviceType


class TestDeviceInfoAppServerUrlV2:

    def test_reads_app_server_url_v2_when_present(self):
        info = TPLinkDeviceInfo({
            "deviceType": "WIRELESSROUTER",
            "appServerUrl": "https://primary.example",
            "appServerUrlV2": "https://v2.example",
        })
        assert info.app_server_url_v2 == "https://v2.example"

    def test_app_server_url_v2_is_none_when_missing(self):
        info = TPLinkDeviceInfo({"deviceType": "IOT.SMARTPLUGSWITCH"})
        assert info.app_server_url_v2 is None


class TestRouterEnum:

    def test_router_enum_value_exists(self):
        assert TPLinkDeviceType.ROUTER.value == 1000

    def test_router_does_not_collide_with_other_values(self):
        values = [m.value for m in TPLinkDeviceType]
        assert len(values) == len(set(values)), "duplicate enum value"


def _make_router_info(status=1, **overrides):
    base = {
        "deviceType": "WIRELESSROUTER",
        "fwVer": "1.6.2 Build 20260119 rel.87654",
        "appServerUrl": "https://v1.example",
        "appServerUrlV2": "https://v2.example",
        "deviceRegion": "ap-southeast-1",
        "deviceId": "ROUTER-DEVICE-ID",
        "deviceName": "Archer AX53",
        "deviceHwVer": "1.0",
        "alias": "My Router",
        "deviceMac": "AABBCCDDEEFF",
        "deviceModel": "Archer AX53(EU)",
        "status": status,
    }
    base.update(overrides)
    return TPLinkDeviceInfo(base)


def _make_router(**overrides):
    from tplinkcloud.router import Router
    info = _make_router_info(**overrides)
    # Router doesn't talk to the network; pass None for the client.
    return Router(client=None, device_id=info.device_id, device_info=info)


class TestRouterMetadata:

    def test_alias(self):
        r = _make_router()
        assert r.get_alias() == "My Router"

    def test_mac(self):
        r = _make_router()
        assert r.mac == "AABBCCDDEEFF"

    def test_firmware_version(self):
        r = _make_router()
        assert r.firmware_version == "1.6.2 Build 20260119 rel.87654"

    def test_hardware_version(self):
        r = _make_router()
        assert r.hardware_version == "1.0"

    def test_region(self):
        r = _make_router()
        assert r.region == "ap-southeast-1"

    def test_app_server_url_v2(self):
        r = _make_router()
        assert r.app_server_url_v2 == "https://v2.example"

    def test_is_online_true_when_status_1(self):
        r = _make_router(status=1)
        assert r.is_online() is True

    def test_is_online_false_when_status_0(self):
        r = _make_router(status=0)
        assert r.is_online() is False

    def test_model_type_is_router(self):
        r = _make_router()
        assert r.model_type == TPLinkDeviceType.ROUTER


class TestRouterUnsupportedActions:

    _METHOD_ARGS = {
        "set_led_state": (True,),
        "get_schedule_rule": ("rule-id",),
        "edit_schedule_rule": ({"id": "rule-id"},),
        "add_schedule_rule": ({"enable": 1},),
        "delete_schedule_rule": ("rule-id",),
        "get_runtime_day": (2026, 4),
        "get_runtime_month": (2026,),
    }

    @pytest.mark.asyncio
    @pytest.mark.parametrize("method_name", [
        "power_on", "power_off", "toggle", "is_on", "is_off",
        "set_led_state",
        "get_sys_info",
        "get_schedule_rules", "get_schedule_rule",
        "edit_schedule_rule", "add_schedule_rule",
        "delete_all_scheduled_rules", "delete_schedule_rule",
        "get_runtime_day", "get_runtime_month",
        "get_net_info", "get_time", "get_timezone",
    ])
    async def test_unsupported_methods_raise(self, method_name):
        r = _make_router()
        method = getattr(r, method_name)
        args = self._METHOD_ARGS.get(method_name, ())
        with pytest.raises(NotImplementedError) as exc_info:
            await method(*args)
        msg = str(exc_info.value)
        assert method_name in msg
        assert "discovery-findings" in msg


class TestPackageReExport:

    def test_router_importable_from_package_root(self):
        from tplinkcloud import Router
        from tplinkcloud.router import Router as RouterDirect
        assert Router is RouterDirect

    def test_router_in_dunder_all(self):
        import tplinkcloud
        assert "Router" in tplinkcloud.__all__
