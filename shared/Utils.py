import time
from random import randint

FIVE_MIN = 60 * 5
ONE_HOUR = 60 * 60
ONE_DAY  = ONE_HOUR * 24

rollup_periods = ['5min', '1hour', '1day']
rollup_periods_display = {
    '5min' : '5 minutes',
    '1hour': '1 hour',
    '1day' : '1 day',
}

def value_generator(n):
    while 1:
        f = n - randint(0, 5)
        if f < 0:
            f = 0
        t = n + randint(0, 10)
        if t > 30:
            t = 30
        n = randint(f, t)
        yield n

def get_date_str_1day(ts):
    return time.strftime('%Y-%m-%d', time.localtime(ts))

def get_date_str_1hour(ts):
    t = ONE_HOUR * (int(ts) / ONE_HOUR)
    return time.strftime('%Y-%m-%d %H', time.localtime(t))

def get_date_str_5min(ts):
    t = FIVE_MIN * (int(ts) / FIVE_MIN)
    return time.strftime('%Y-%m-%d %H:%M', time.localtime(t))

date_str_functions = {
    '5min'  : get_date_str_5min,
    '1hour' : get_date_str_1hour,
    '1day'  : get_date_str_1day,
}

def get_date_str(rollup_period, timestamp):
    return date_str_functions[rollup_period](timestamp)

