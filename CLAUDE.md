# tplink-cloud-api

Python library for controlling TP-Link Kasa smart home devices remotely via the TP-Link Cloud API. Unlike local-network libraries, this works from anywhere with an internet connection.

## Quick start

```bash
# Install
pip3 install -e .

# Run tests (requires Docker)
docker compose up -d
pytest --verbose
```

## Architecture

### V2 Cloud API flow

1. **Account status** (`/api/v2/account/getAccountStatusAndUrl`) — resolves the regional API server URL
2. **Login** (`/api/v2/account/login`) — authenticates with TP-Link credentials, returns token + refresh token
3. **Device operations** — POST to `/` on the device's `appServerUrl` with V2 signing headers

All V2 requests use HMAC-SHA1 signing (see `tplinkcloud/signing.py`). The signing keys are app-level constants extracted from the Kasa Android APK — they are not secrets.

### Key modules

| Module | Purpose |
|---|---|
| `client.py` | Synchronous HTTP client for auth (login, MFA, refresh, device list) |
| `device_client.py` | Async HTTP client (aiohttp) for device operations with V2 signing |
| `device_manager.py` | Main entry point — `TPLinkDeviceManager` handles auth + device construction |
| `signing.py` | HMAC-SHA1 request signing for V2 API |
| `exceptions.py` | `TPLinkAuthError`, `TPLinkMFARequiredError`, `TPLinkTokenExpiredError`, `TPLinkCloudError`, `TPLinkDeviceOfflineError` |
| `certs/` | TP-Link private CA cert chain (V2 API servers use their own CA) |

### Device class hierarchy

`TPLinkDevice` is the base class (on/off/toggle). Specialized subclasses add features:

- **Plugs/switches**: `HS100`, `HS103`, `HS105`, `HS200` — basic on/off
- **Energy monitoring**: `HS110`, `KP115`, `KP125` (extend `EmeterDevice`)
- **Power strips**: `HS300`, `KP303` — parent + child devices per outlet
- **Outdoor plugs**: `KP200`, `KP400` — parent + child devices per outlet, `EP40` — single outlet
- **Light strips**: `KL420L5`, `KL430` — color, brightness, color temp via `smartlife.iot.smartbulb.lightingservice`

Devices with multiple outlets (`HS300`, `KP303`, `KP200`, `KP400`) have `has_children() -> True`. Child devices are separate class instances (e.g., `HS300Child`) with a `child_id`.

### Adding a new device

1. Create `tplinkcloud/<model>.py` extending `TPLinkDevice` (or `EmeterDevice` for energy monitoring)
2. Define the `DeviceType` enum value in `device_type.py`
3. Add the model mapping in `device_manager.py` `_construct_device()`
4. Add wiremock stubs in `tests/wiremock/mappings/` and `tests/wiremock/__files/`
5. Add tests in `tests/test_device_manager.py`

## Controlling devices

```python
import asyncio
from tplinkcloud import TPLinkDeviceManager

device_manager = TPLinkDeviceManager('kasa@email.com', 'password')

async def main():
    devices = await device_manager.get_devices()
    for device in devices:
        print(f'{device.model_type.name}: {device.get_alias()}')

    # Find and control a device by name
    plug = await device_manager.find_device('Living Room Lamp')
    if plug:
        await plug.toggle()        # toggle on/off
        await plug.power_on()      # turn on
        await plug.power_off()     # turn off

    # Light strips
    strip = await device_manager.find_device('LED Strip')
    if strip:
        await strip.set_brightness(75)
        await strip.set_color(hue=240, saturation=100, brightness=80)
        await strip.set_color_temp(4000)

    # Energy monitoring (HS110, KP115, KP125)
    plug = await device_manager.find_device('Energy Plug')
    if plug:
        usage = await plug.get_power_usage_realtime()

asyncio.run(main())
```

## Testing

Tests use WireMock to mock the TP-Link Cloud API. The wiremock service runs in Docker.

```bash
docker compose up -d        # start wiremock
pytest --verbose             # run all tests
pytest tests/test_hs300.py   # run one test file
```

### Test environment variables

These are set in `tests/local_env_vars.py` and must match the wiremock stubs:

- `TPLINK_KASA_USERNAME`: `kasa_docker`
- `TPLINK_KASA_PASSWORD`: `kasa_password`
- `TPLINK_KASA_TERM_ID`: `2a8ced52-f200-4b79-a1fe-2f6b58193c4c`
- `TPLINK_KASA_API_URL`: `http://127.0.0.1:8080`

### Wiremock stubs

- `tests/wiremock/mappings/` — request matchers (URL, headers, body patterns)
- `tests/wiremock/__files/` — response bodies (JSON)

Mappings use `"urlPath": "/"` with body pattern matching. Headers use `"matches"` for flexible User-Agent and Content-Type matching.

## Project tracking

- GitHub Project: https://github.com/users/piekstra/projects/2
- Wiki (API reference, architecture): https://github.com/piekstra/tplink-cloud-api/wiki
