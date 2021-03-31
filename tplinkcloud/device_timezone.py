class DeviceTimezone:

    def __init__(self, timezone):
        # Truly no idea what list of timezones these index
        self.index = timezone.get('index')
        self.err_code = timezone.get('err_code')
