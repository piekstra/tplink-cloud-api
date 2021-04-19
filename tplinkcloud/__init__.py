from .device_manager import TPLinkDeviceManager
from .device_manager_power_tools import TPLinkDeviceManagerPowerTools
from .device_schedule_rule_builder import TPLinkDeviceScheduleRuleBuilder

__all__ = [
    'TPLinkDeviceManager',
    'TPLinkDeviceManagerPowerTools',
    'TPLinkDeviceScheduleRuleBuilder',
]

# Windows OS-specific HACK to silence exception thrown on event loop being closed
# as part of the asyncio library's proactor
# Hack sourced from an issue on the aiohttp library:
#   https://github.com/aio-libs/aiohttp/issues/4324#issuecomment-733884349
# This assumes you have the asyncio library installed
import platform
if platform.system() == 'Windows':
    from functools import wraps
    from asyncio.proactor_events import _ProactorBasePipeTransport

    def silence_event_loop_closed(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except RuntimeError as e:
                if str(e) != 'Event loop is closed':
                    raise
        return wrapper

    _ProactorBasePipeTransport.__del__ = silence_event_loop_closed(_ProactorBasePipeTransport.__del__)
