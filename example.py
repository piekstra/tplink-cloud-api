from tplinkcloud import TPLinkDeviceManager

import json

username='user@email.com'
password='redacted'

device_manager = TPLinkDeviceManager(username, password, verbose=True)
devices = device_manager.get_devices()
if devices:
  print(f'Found {len(devices)} devices')
  for device in devices:
    print(f'{device.model_type.name} device called {device.get_alias()}')
  
device_names_like = "plug"
devices = device_manager.find_devices(device_names_like)
if devices:
  print(f'Found {len(devices)} matching devices')
  for device in devices:
    print(f'{device.model_type.name} device called {device.get_alias()}')

device_name = 'Desk Light'
device = device_manager.find_device(device_name)
if device:
  print(f'Found {device.model_type.name} device: {device_name}')
  device.power_on()
  result = device.is_on()
  print(json.dumps(result, indent=2))
  result = device.is_off()
  print(json.dumps(result, indent=2))

  device.power_off()
  result = device.is_on()
  print(json.dumps(result, indent=2))
  result = device.is_off()
  print(json.dumps(result, indent=2))

  result = device.get_power_usage()
  print(json.dumps(result, indent=2))

  result = device.get_sys_info()
  print(json.dumps(result, indent=2))

  result = device.get_schedule_rules()
  print(json.dumps(result, indent=2))

  # device.set_led_state(False)

  # device.edit_schedule_rule()
else:  
  print(f'Could not find {device_name}')