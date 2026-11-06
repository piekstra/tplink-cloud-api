"""TP-Link Router device class.

NOTE: TP-Link routers cannot be controlled through the TP-Link Cloud API
that powers this library. They use the proprietary TMP binary protocol,
reachable only via local-network TCP or a persistent device-to-cloud
mTLS tunnel. See docs/superpowers/router-api/discovery-findings.md for
the evidence and reasoning.

This class therefore surfaces router metadata only and raises
NotImplementedError on plug-style action methods. For local control,
use a dedicated local-network library (e.g. python-kasa).
"""
from .device import TPLinkDevice
from .device_type import TPLinkDeviceType


_UNSUPPORTED_MSG_FMT = (
    "Router.{method}() is not supported. TP-Link routers cannot be "
    "controlled via the cloud API. See "
    "docs/superpowers/router-api/discovery-findings.md."
)


def _unsupported(method_name: str) -> NotImplementedError:
    return NotImplementedError(_UNSUPPORTED_MSG_FMT.format(method=method_name))


class Router(TPLinkDevice):
    """A TP-Link router (wireless or xDSL modem-router) recognized via the
    cloud device-list API. Surfaces metadata only — see module docstring."""

    def __init__(self, client, device_id, device_info, child_id=None):
        super().__init__(client, device_id, device_info, child_id=child_id)
        self.model_type = TPLinkDeviceType.ROUTER

    # ---- metadata accessors ----

    @property
    def mac(self):
        return self.device_info.device_mac

    @property
    def firmware_version(self):
        return self.device_info.fw_ver

    @property
    def hardware_version(self):
        return self.device_info.device_hw_ver

    @property
    def region(self):
        return self.device_info.device_region

    @property
    def app_server_url_v2(self):
        return self.device_info.app_server_url_v2

    def is_online(self) -> bool:
        return self.device_info.status == 1

    # ---- explicitly unsupported actions ----

    async def power_on(self):
        raise _unsupported("power_on")

    async def power_off(self):
        raise _unsupported("power_off")

    async def toggle(self):
        raise _unsupported("toggle")

    async def is_on(self):
        raise _unsupported("is_on")

    async def is_off(self):
        raise _unsupported("is_off")

    async def set_led_state(self, on):
        raise _unsupported("set_led_state")

    async def get_sys_info(self):
        raise _unsupported("get_sys_info")

    async def get_schedule_rules(self):
        raise _unsupported("get_schedule_rules")

    async def get_schedule_rule(self, rule_id):
        raise _unsupported("get_schedule_rule")

    async def edit_schedule_rule(self, rule):
        raise _unsupported("edit_schedule_rule")

    async def add_schedule_rule(self, rule):
        raise _unsupported("add_schedule_rule")

    async def delete_all_scheduled_rules(self):
        raise _unsupported("delete_all_scheduled_rules")

    async def delete_schedule_rule(self, rule_id):
        raise _unsupported("delete_schedule_rule")

    async def get_runtime_day(self, year, month):
        raise _unsupported("get_runtime_day")

    async def get_runtime_month(self, year):
        raise _unsupported("get_runtime_month")

    async def get_net_info(self):
        raise _unsupported("get_net_info")

    async def get_time(self):
        raise _unsupported("get_time")

    async def get_timezone(self):
        raise _unsupported("get_timezone")
