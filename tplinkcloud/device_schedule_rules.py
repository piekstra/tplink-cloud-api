from enum import Enum

class DeviceScheduleRuleStartOption(Enum):
    Time = 0
    Sunrise = 1
    Sunset = 2

class DeviceScheduleRule:
    
    def __init__(self, rule):
        self.id = rule.get('id')
        self.name = rule.get('name')
        self.enable = rule.get('enable')
        self.wday = rule.get('wday')
        # Options are as follows:
        #   0 - Start at a particular time
        #   1 - Start at Sunrise
        #   2 - Start at Sunset
        self.stime_opt = rule.get('stime_opt')
        self.soffset = rule.get('soffset')
        # This is in minutes into the day
        # There are 1440 minutes in a day
        self.smin = rule.get('smin')
        # If turning on the device, this will be 1
        self.sact = rule.get('sact')
        self.etime_opt = rule.get('etime_opt')
        self.eoffset = rule.get('eoffset')
        self.emin = rule.get('emin')
        self.eact = rule.get('eact')
        self.repeat = rule.get('repeat')
        # The following three are specified when 'repeat' is not enabled
        self.year = rule.get('year')
        self.month = rule.get('month')
        self.day = rule.get('day')

        # Add in some custom "convenience" attributes
        # These deviate from the raw information but add convenience
        if self.enable is not None:
            self.enabled = True if self.enable == 1 else False

        if self.wday is not None and isinstance(self.wday, list) and len(self.wday) == 7:
            self.sunday_enabled = True if self.wday[0] == 1 else False
            self.monday_enabled = True if self.wday[1] == 1 else False
            self.tuesday_enabled = True if self.wday[2] == 1 else False
            self.wednesday_enabled = True if self.wday[3] == 1 else False
            self.thursday_enabled = True if self.wday[4] == 1 else False
            self.friday_enabled = True if self.wday[5] == 1 else False
            self.saturday_enabled = True if self.wday[6] == 1 else False
        
        if self.stime_opt is not None:
            self.start_type = DeviceScheduleRuleStartOption(self.stime_opt)

        if self.sact is not None:
            self.turn_on = True if self.sact == 1 else False
            self.turn_off = not self.turn_on

        if self.repeat is not None:
            self.repeated = True if self.repeat == 1 else False
        if self.smin is not None:
            # Since year, month, day should be specified here, 
            # create new time values based on `smin`
            self.hour = self.smin // 60
            self.minute = self.smin % 60

    # These are the values expected and returned by the TP-Link API
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'enable': self.enable,
            'wday': self.wday,
            'stime_opt': self.stime_opt,
            'soffset': self.soffset,
            'smin': self.smin,
            'sact': self.sact,
            'etime_opt': self.etime_opt,
            'eoffset': self.eoffset,
            'emin': self.emin,
            'eact': self.eact,
            'repeat': self.repeat,
            'year': self.year,
            'month': self.month,
            'day': self.day,
        }

class DeviceScheduleRules:
    
    def __init__(self, rules):
        rule_list = rules.get('rule_list')
        if rule_list:
            self.rules = [DeviceScheduleRule(rule) for rule in rule_list]
        else:
            self.rules = []
        self.version = rules.get('version')
        self.enable = rules.get('enable')
        self.err_code = rules.get('err_code')
    
