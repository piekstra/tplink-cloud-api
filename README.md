# tplink-cloud-api

Control TP-Link Kasa smart home devices from anywhere over the internet using TP-Link's cloud API — no local network access required.

## Why cloud control?

Most TP-Link/Kasa Python libraries (like [python-kasa](https://github.com/python-kasa/python-kasa)) communicate with devices over your **local network**. That works great when your code runs at home, but not when it runs somewhere else.

This library uses the **TP-Link Cloud API** instead, so your code can control devices from anywhere with an internet connection. That makes it the right choice for:

- **Server-side automations** — cloud functions, cron jobs, CI pipelines
- **Web service integrations** — [IFTTT](https://ifttt.com/), [Thinger.io](https://thinger.io/), webhooks
- **Mobile scripting** — Tasker (Android), Shortcuts (iOS)
- **Remote access** — control devices while you're away from home

If you just need local control on the same network as your devices, [python-kasa](https://github.com/python-kasa/python-kasa) is a great option with broader device support.

## How it works

The library authenticates with your TP-Link / Kasa account credentials using the **V2 TP-Link Cloud API** with HMAC-SHA1 request signing. It supports MFA (two-factor authentication) and automatic refresh token management.

Originally a Python port of [Adumont's Node.js module](https://github.com/adumont/tplink-cloud-api).

## Device Compatibility

The following devices are _officially_ supported by the library at this time:

**Smart Plugs**
* HS100 (Smart Plug - Blocks two outlets as a single outlet)
* HS103 (Smart Plug Lite - 12 Amp)
* HS105 (Smart Plug Mini - 15 Amp)
* HS110 (Smart Plug with Energy Monitoring)
* KP115 (Smart Plug with Energy Monitoring - 15 Amp; replacement for HS110)
* KP125 (Smart Plug Mini with Energy Monitoring)
* EP40 (Outdoor Smart Plug)

**Smart Switches**
* HS200 (Smart Light Switch)

**Smart Power Strips**
* HS300 (Smart Plug Power Strip with 6 Smart Outlets)
* KP303 (Smart Plug Power Strip with 3 Outlets)

**Smart Outdoor Plugs (Multi-Outlet)**
* KP200 (Smart Outdoor Plug with 2 Outlets)
* KP400 (Smart Outdoor Plug with 2 Outlets)

**Smart Light Strips**
* KL420L5 (Smart LED Light Strip)
* KL430 (Smart Light Strip, Multicolor)

Devices not explicitly listed above will still work with basic on/off functionality through the generic `TPLinkDevice` class.

## Requirements

* Python 3.10+

## Installation

The package is available via PyPi and can be installed with the following command:
```
pip3 install tplink-cloud-api
```

To install it from the repo, clone the repo and cd into the directory:

```
git clone https://github.com/piekstra/tplink-cloud-api.git
cd tplink-cloud-api
```

You can install this library with `pip`:

```
pip3 install .
```

## Usage

### Authenticate

Instantiating a `TPLinkDeviceManager` automatically logs in with your TP-Link / Kasa credentials using the V2 API, caches the login token, and fetches your devices.

```python
from tplinkcloud import TPLinkDeviceManager

username = 'kasa@email.com'
password = 'secure'

device_manager = TPLinkDeviceManager(username, password)
```

> Note that the device manager can also be constructed using `await` if desired and running in an `async` context

#### MFA (Two-Factor Authentication)

If your TP-Link account has two-factor authentication enabled, you can provide an `mfa_callback` function that will be called when MFA verification is needed:

```python
def handle_mfa(mfa_type, email):
    """Called when MFA is required. Returns the verification code."""
    return input(f'Enter the MFA code sent to {email}: ')

device_manager = TPLinkDeviceManager(
    username='kasa@email.com',
    password='secure',
    mfa_callback=handle_mfa,
)
```

#### Token Management

The library automatically handles refresh tokens. You can also manually manage tokens for session persistence:

```python
# Get tokens for later use
token = device_manager.get_token()
refresh_token = device_manager.get_refresh_token()

# Resume a session without re-authenticating
device_manager = TPLinkDeviceManager(prefetch=False)
device_manager.set_auth_token(token)
device_manager.set_refresh_token(refresh_token)
```

#### Error Handling

The library provides specific exception classes for common error scenarios:

```python
from tplinkcloud import (
    TPLinkDeviceManager,
    TPLinkAuthError,
    TPLinkMFARequiredError,
    TPLinkTokenExpiredError,
    TPLinkCloudError,
)

try:
    device_manager = TPLinkDeviceManager(username, password)
except TPLinkAuthError:
    print('Wrong username or password')
except TPLinkMFARequiredError as e:
    print(f'MFA required (type: {e.mfa_type}), provide an mfa_callback')
except TPLinkCloudError as e:
    print(f'API error: {e} (code: {e.error_code})')
```

### Async Context

In order to run the async methods, you will need an async context. For a simple Python script, you can simply use the following:

```python
import asyncio

asyncio.run(example_async_method())
```

For more advanced usage, you can gather tasks so they all run at once such as in the following example which can fetch a large number of devices' system info very quickly:

```python
from tplinkcloud import TPLinkDeviceManager

import asyncio
import json

username = 'kasa@email.com'
password = 'secure'
device_manager = TPLinkDeviceManager(username, password)

async def fetch_all_devices_sys_info():
  devices = await device_manager.get_devices()
  fetch_tasks = []
  for device in devices:
    async def get_info(device):
      print(f'Found {device.model_type.name} device: {device.get_alias()}')
      print("SYS INFO")
      print(json.dumps(device.device_info, indent=2, default=lambda x: vars(x)
                        if hasattr(x, "__dict__") else x.name if hasattr(x, "name") else None))
      print(json.dumps(await device.get_sys_info(), indent=2, default=lambda x: vars(x)
                        if hasattr(x, "__dict__") else x.name if hasattr(x, "name") else None))
    fetch_tasks.append(get_info(device))
  await asyncio.gather(*fetch_tasks)

asyncio.run(fetch_all_devices_sys_info())
```

### Retrieve devices

To view your devices, you can run the following:

```python
devices = await device_manager.get_devices()
if devices:
  print(f'Found {len(devices)} devices')
  for device in devices:
    print(f'{device.model_type.name} device called {device.get_alias()}')
```

### Control your devices

#### Smart Power Strips (HS300, KP303)

Toggle a plug:

```python
device_name = "My Smart Plug"
device = await device_manager.find_device(device_name)
if device:
  print(f'Found {device.model_type.name} device: {device.get_alias()}')
  await device.toggle()
else:
  print(f'Could not find {device_name}')
```

Replace `My Smart Plug` with the alias you gave to your plug in the Kasa app (be sure to give a different alias to each device). Instead of `toggle()`, you can also use `power_on()` or `power_off()`.

To retrieve power consumption data for one of the individual plugs on an HS300 power strip (KP303 does not support power usage data):

```python
import json
device = await device_manager.find_device("My Smart Plug")
power_usage = await device.get_power_usage_realtime()
print(json.dumps(power_usage, indent=2, default=lambda x: x.__dict__))
```

If you want to get multiple devices with a name including a certain substring, you can use the following:

```python
device_names_like = "plug"
devices = await device_manager.find_devices(device_names_like)
if devices:
  print(f'Found {len(devices)} matching devices')
  for device in devices:
    print(f'{device.model_type.name} device called {device.get_alias()}')
```

#### Smart Plugs (HS100, HS103, HS105, HS110, KP115, KP125, EP40)

These have the same functionality as the Smart Power Strips, though the HS100, HS103, and HS105 do not have the power usage features.

#### Smart Outdoor Plugs (KP200, KP400)

Multi-outlet outdoor plugs. Each outlet is exposed as a child device that can be controlled independently:

```python
# Control the parent device (affects all outlets)
device = await device_manager.find_device("Backyard Plug")
await device.power_on()

# Child devices are returned by get_devices() alongside parents
devices = await device_manager.get_devices()
for device in devices:
  if 'KP400CHILD' in device.model_type.name:
    print(f'Outlet: {device.get_alias()}')
    await device.toggle()
```

#### Smart Light Strips (KL420L5, KL430)

Light strips support color and brightness control:

```python
device = await device_manager.find_device("Living Room Strip")

# Basic on/off
await device.power_on()

# Set brightness (0-100)
await device.set_brightness(75)

# Set color (hue: 0-360, saturation: 0-100, brightness: 0-100)
await device.set_color(hue=240, saturation=100, brightness=80)

# Set color temperature (2500-9000 Kelvin)
await device.set_color_temp(4000)
```

#### Smart Switches (HS200)

Smart switches have the same on/off functionality as smart plugs:

```python
device = await device_manager.find_device("Kitchen Light Switch")
await device.toggle()
```

### Add and modify schedule rules for your devices

Edit an existing schedule rule

```python
device_name = "My Smart Plug"
device = await device_manager.find_device(device_name)
if device:
  print(f'Found {device.model_type.name} device: {device.get_alias()}')
  print(f'Modifying schedule rule')
  schedule = await device.get_schedule_rules()
  original_rule = schedule.rules[0]
  rule_edit = TPLinkDeviceScheduleRuleBuilder(
    original_rule
  ).with_enable_status(
      False
  )
  await device.edit_schedule_rule(rule_edit.to_json())
else:
  print(f'Could not find {device_name}')
```

Add a new schedule rule

```python
device_name = "My Smart Plug"
device = await device_manager.find_device(device_name)
if device:
  print(f'Found {device.model_type.name} device: {device.get_alias()}')
  print(f'Adding schedule rule')
  new_rule = TPLinkDeviceScheduleRuleBuilder(
  ).with_action(
      turn_on=True
  ).with_name(
      'My Schedule Rule'
  ).with_enable_status(
      True
  ).with_sunset_start().with_repeat_on_days(
      [0, 0, 0, 0, 0, 1, 1]
  ).build()
  await device.add_schedule_rule(new_rule.to_json())
else:
  print(f'Could not find {device_name}')
```

Delete a schedule rule

```python
device_name = "My Smart Plug"
device = await device_manager.find_device(device_name)
if device:
  print(f'Found {device.model_type.name} device: {device.get_alias()}')
  print(f'Deleting schedule rule')
  schedule = await device.get_schedule_rules()
  rule = schedule.rules[0]
  await device.delete_schedule_rule(rule.id)
else:
  print(f'Could not find {device_name}')
```

### Testing

This project leverages `wiremock` to test the code to some extent. Note this will not protect the project from changes that TP-Link makes to their API, but instead verifies that the existing code functions consistently as written.

#### Local Testing

Note that the tests setup leverages the [`local_env_vars.py`](tests/local_env_vars.py) file. The values for those environment variables need to be set based on the following:

* `TPLINK_KASA_USERNAME`: `kasa_docker` - This must have parity with the V2 login `body` specified in [`tests/wiremock/mappings/v2_login_request.json`](tests/wiremock/mappings/v2_login_request.json)
* `TPLINK_KASA_PASSWORD`: `kasa_password` - This must have parity with the V2 login `body` specified in [`tests/wiremock/mappings/v2_login_request.json`](tests/wiremock/mappings/v2_login_request.json)
* `TPLINK_KASA_TERM_ID`: `2a8ced52-f200-4b79-a1fe-2f6b58193c4c` - This must be a UUID V4 string and must have parity with the V2 login `body` specified in [`tests/wiremock/mappings/v2_login_request.json`](tests/wiremock/mappings/v2_login_request.json)
* `TPLINK_KASA_API_URL`: `http://127.0.0.1:8080` - This URL is simply `http://127.0.0.1` but the url port must have parity with the [`docker-compose.yaml`](docker-compose.yaml) wiremock service's exposed http `port`.

To run tests, you will first need to start the wiremock service by running:

```
docker compose up -d
```

Then, you can run the actual tests with the following command:

```
pytest --verbose
```

#### GitHub Testing

This project leverages GitHub Actions and has a [workflow](.github/workflows/python-package.yml) that will run these tests. The environment configuration for the tests must have parity with the [`local_env_vars.py`](tests/local_env_vars.py) file from the [local testing](#local-testing).
