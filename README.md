# tplink-cloud-api
A Python library to remotely control TP-Link smart home devices using their cloud service - no need to be on the same network as your devices

This started as a Python port of Adumont's Node.js module:
https://github.com/adumont/tplink-cloud-api

# Introduction

The `tplinkcloud` Python module allows you to remotely control your TP-Link smartplugs (HS100, HS103, HS105, HS110, HS300, KP115) using the TP-Link cloud web service, from anywhere, without the need to be on the same wifi/lan.

It's especially useful in scenarios where you want to control your devices from public web services, like [IFTTT](https://ifttt.com/), [Thinger.io](https://thinger.io/), [Webtask.io](https://webtask.io/), [Glitch.com](http://glitch.com/), Tasker (Android)...

# Device Compatibility

The following devices are _officially_ supported by the library at this time:
* HS300 (Smart Plug Power Strip with 6 Smart Outlets)
* HS100 (Older Smart Plug - Blocks two outlets as a single outlet)
* HS103 (Smaller Single-Socket Smart Plug - 12 Amp)
* HS105 (Smaller Single-Socket Smart Plug - 15 Amp)
* HS110 (Older Smart Plug - Blocks two outlets as a single outlet)
* KP115 (Small Single-Socket Smart Plug - 15 Amp; replacement for HS110)
* KP303 (Smart Plug Power Strip with 3 Outlets)

# Installation

The package is availble via PyPi and can be installed with the following command:
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

# Usage

## Authenticate

Instantiating a TP Link Device Manager automatically logs in with your TP-Link credentials, caches the login token, and fetches your devices. The current TP-Link Cloud API Url (https://wap.tplinkcloud.com) is assumed if not provided explicitly.

```python
from tplinkcloud import TPLinkDeviceManager

username='kasa@email.com'
password='secure'

device_manager = TPLinkDeviceManager(username, password)
```

> Note that the device manager can also be constructed using `await` if desired and running in an `async` context

## Async Context

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

## Retrieve devices

To view your devices, you can run the following:

```python
devices = await device_manager.get_devices()
if devices:
  print(f'Found {len(devices)} devices')
  for device in devices:
    print(f'{device.model_type.name} device called {device.get_alias()}')
```

## Control your devices

### Smart Power Strips (HS300, KP303)

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

### Smart Plugs (Not Power Strips) (HS100, HS103, HS105, HS110, KP115)

These have the same functionality as the Smart Power Strips, though the HS100, HS103 and HS105 do not have the power usage features.

## Add and modify schedule rules for your devices

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

## Testing

This project leverages `wiremock` to test the code to some extent. Note this will not protect the project from changes that TP-Link makes to their API, but instead verifies that the existing code functions consistently as written.

### Local Testing 

Note that the tests setup leverages the [`local_env_vars.py`](tests/local_env_vars.py) file. The values for those environment variables need to be set based on the following:

* `TPLINK_KASA_USERNAME`: `kasa_docker` - This must have parity with the `login` `body` specified in [`tests/wiremock/mappings/login_request.json`](tests/wiremock/mappings/login_request.json)
* `TPLINK_KASA_PASSWORD`: `kasa_password` - This must have parity with the `login` `body` specified in [`tests/wiremock/mappings/login_request.json`](tests/wiremock/mappings/login_request.json)
* `TPLINK_KASA_TERM_ID`: `2a8ced52-f200-4b79-a1fe-2f6b58193c4c` - This must be a UUID V4 string and must have parity with the `login` `body` specified in [`tests/wiremock/mappings/login_request.json`](tests/wiremock/mappings/login_request.json). It must also match the `termID` query parameter in all mocked requests found [here](tests/wiremock/mappings)
* `TPLINK_KASA_API_URL`: `http://127.0.0.1:8080` - This URL is simply `http://127.0.0.1` but the url port must have parity with the [`docker-compose.yaml`](docker-compose.yaml) wiremock service's exposed http `port`. 

To run tests, you will first need to start the wiremock service by running:

```
docker-compose up -d
```

Then, you can run the actual tests with the following command:

```
pytest --verbose
```

### GitHub Testing

This project leverages GitHub Actions and has a [workflow](.github/workflows/python-package.yml) that will run these tests. The environment configuration for the tests must have parity with the [`local_env_vars.py`](tests/local_env_vars.py) file from the [local testing](#local-testing).
