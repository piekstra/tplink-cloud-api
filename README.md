# tplink-cloud-api
A Python library to remotely control TP-Link smart home devices using their cloud service - no need to be on the same network as your devices

This is a Python port of Adumont's Node.js module:
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

## Retrieve devices

To view your devices, you can run the following:

```python
devices = device_manager.get_devices()
if devices:
  print(f'Found {len(devices)} devices')
  for device in devices:
    print(f'{device.model_type.name} device called {device.get_alias()}')
```

## Control your devices

### Smart Power Strips (HS300)

Toggle a plug:

```python
device_name = "My Smart Plug"
device = device_manager.find_device(device_name)
if device:
  print(f'Found {device.model_type.name} device: {device.get_alias()}')
  device.toggle()
else:  
  print(f'Could not find {device_name}')
```

Replace `My Smart Plug` with the alias you gave to your plug in the Kasa app (be sure to give a different alias to each device). Instead of `toggle()`, you can also use `power_on()` or `power_off()`.

To retrieve power consumption data for one of the individual plugs on the power strip:

```python
import json
power_usage = device_manager.find_device("My Smart Plug").get_power_usage()
print(json.dumps(power_usage, indent=2, default=lambda x: x.__dict__))
```

If you want to get multiple devices with a name including a certain substring, you can use the following:

```python
device_names_like = "plug"
devices = device_manager.find_devices(device_names_like)
if devices:
  print(f'Found {len(devices)} matching devices')
  for device in devices:
    print(f'{device.model_type.name} device called {device.get_alias()}')
```

### Smart Plugs (Not Power Strips) (HS100, HS103, HS105, HS110, KP115)

These have the same functionality as the Smart Power Strips, though the HS103 and HS105 do not have the power usage features.
