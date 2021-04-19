from .device_schedule_rules import DeviceScheduleRule, DeviceScheduleRuleStartOption


def buildermethod(func):
  def wrapper(self, *args, **kwargs):
    func(self, *args, **kwargs)
    return self
  return wrapper

# Allows an existing rule class to be modified, or a new rule to be built
# This should be used in combination with a device's edit or add schedule
# rule functionality
class TPLinkDeviceScheduleRuleBuilder:

    def __init__(self, rule=None):
        # Create an empty rule if non provided
        if rule:
            self._rule = rule
        else:
            self._rule = DeviceScheduleRule({})
            # This is the default set by the Kasa app
            self._rule.name = 'Schedule Rule'
            # At this time it is best to leave these values as
            # they are given that the Kasa app does not expose
            # the ability to change them
            self._rule.etime_opt = -1
            self._rule.emin = 0
            self._rule.eact = -1

    @buildermethod
    # Whether the device should be turned on or off
    def with_action(self, turn_on):
        self._rule.sact = 1 if turn_on else 0
    
    @buildermethod
    # The name of the rule (not required and not currently visible via the app)
    def with_name(self, name):
        self._rule.name = name

    @buildermethod
    # Whether the rule should be enabled
    def with_enable_status(self, enabled):
        self._rule.enable = 1 if enabled else 0

    @buildermethod
    # What time of day the rule should trigger
    # Overrides other time-of-day triggers
    def with_time_start(self, time):
        self._rule.stime_opt = DeviceScheduleRuleStartOption.Time.value
        self._rule.smin = time.hour * 60 + time.minute

    @buildermethod
    # Set the rule to trigger at sunrise
    # Overrides other time-of-day triggers
    def with_sunrise_start(self):
        self._rule.stime_opt = DeviceScheduleRuleStartOption.Sunrise.value

    @buildermethod
    # Set the rule to trigger at sunset
    # Overrides other time-of-day triggers
    def with_sunset_start(self):
        self._rule.stime_opt = DeviceScheduleRuleStartOption.Sunset.value

    @buildermethod
    # days should be an array of 1's and 0's indicating whether to 
    # apply the rule on a particular day
    # Example:
    #   [1, 1, 0, 0, 0, 0, 0]
    # Means that the rule should be applied every Sunday and Monday
    # Overrides one-run rules
    def with_repeat_on_days(self, days):   
        self._rule.repeat = 1     
        self._rule.wday = days

    @buildermethod
    # What one-day should the rule run (the app only allows current/next day)
    # Overrides repeat days
    def with_one_run(self, time):
        self._rule.repeat = 0
        self._rule.wday = [0, 0, 0, 0, 0, 0, 0]
        self._rule.year = time.year
        self._rule.month = time.month
        self._rule.day = time.day

    @buildermethod
    # This actually doesn't do anything other than validate the
    # state of the rule being built. This is important when adding
    # a new rule
    def build(self):
        if self._rule.name is None:
            raise RuntimeError('Rule name is required')
        if self._rule.sact is None:
            raise RuntimeError('Rule action (sact) is required')
        if self._rule.enable is None:
            raise RuntimeError('Rule enable status is required')
        if self._rule.repeat is None:
            raise RuntimeError('Rule repeat status is required')
        if self._rule.wday is None:
            raise RuntimeError('Rule repeat days (wday) is required')

    # These are the values expected and returned by the TP-Link API
    # Not all values are required
    def to_json(self):
        obj_json = {}
        if self._rule.id is not None:
            obj_json['id'] = self._rule.id
        if self._rule.name is not None:
            obj_json['name'] = self._rule.name
        if self._rule.enable is not None:
            obj_json['enable'] = self._rule.enable
        if self._rule.wday is not None:
            obj_json['wday'] = self._rule.wday
        if self._rule.stime_opt is not None:
            obj_json['stime_opt'] = self._rule.stime_opt
        if self._rule.soffset is not None:
            obj_json['soffset'] = self._rule.soffset
        if self._rule.smin is not None:
            obj_json['smin'] = self._rule.smin
        if self._rule.sact is not None:
            obj_json['sact'] = self._rule.sact
        if self._rule.etime_opt is not None:
            obj_json['etime_opt'] = self._rule.etime_opt
        if self._rule.eoffset is not None:
            obj_json['eoffset'] = self._rule.eoffset
        if self._rule.emin is not None:
            obj_json['emin'] = self._rule.emin
        if self._rule.eact is not None:
            obj_json['eact'] = self._rule.eact
        if self._rule.repeat is not None:
            obj_json['repeat'] = self._rule.repeat
        if self._rule.year is not None:
            obj_json['year'] = self._rule.year
        if self._rule.month is not None:
            obj_json['month'] = self._rule.month
        if self._rule.day is not None:
            obj_json['day'] = self._rule.day
        return obj_json
