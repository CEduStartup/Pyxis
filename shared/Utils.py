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

def time_round(ts, period='1day'):
    d = None
    if period == '1day':
        d = ONE_DAY
    elif period == '1hour':
        d = ONE_HOUR
    elif period == '5min':
        d = FIVE_MIN
    else:
        raise ValueError('`period` must be `1day`, `1hour` or `5min`')
    return d * (int(ts) / d)

def str2time(string):
    try:
        return time.mktime(time.strptime(string, '%Y-%m-%d'))
    except:
        raise ValueError('Date `%s` does not match format `%Y-%m-%d`.')

def get_date_str_1day(ts):
    return time.strftime('%Y-%m-%d', time.localtime(ts))

def get_date_str_1hour(ts):
    t = time_round(ts, '1hour')
    return time.strftime('%Y-%m-%d %H', time.localtime(t))

def get_date_str_5min(ts):
    t = time_round(ts, '5min')
    return time.strftime('%Y-%m-%d %H:%M', time.localtime(t))

date_str_functions = {
    '5min'  : get_date_str_5min,
    '1hour' : get_date_str_1hour,
    '1day'  : get_date_str_1day,
}

def get_date_str(rollup_period, timestamp):
    return date_str_functions[rollup_period](timestamp)
