class DeviceTime:
    
    def __init__(self, time):
        self.year = time.get('year')
        self.month = time.get('month')
        self.mday = time.get('mday')
        self.hour = time.get('hour')
        self.min = time.get('min')
        self.sec = time.get('sec')
        self.err_code = time.get('err_code')
