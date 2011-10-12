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
    t = time.localtime(ts)
    if period == '1day':
        t = (t.tm_year, t.tm_mon, t.tm_mday, 0, 0, 0, -1, -1, -1)
    elif period == '1hour':
        t = (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, 0, 0, -1, -1, -1)
    elif period == '5min':
        tm_min = 5 * (t.tm_min / 5)
        t = (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, tm_min, 0, -1, -1, -1)
    else:
        raise ValueError('`period` must be `1day`, `1hour` or `5min`')
    return time.mktime(t)

def str2time(string):
    try:
        t = time.strptime(string, '%Y-%m-%d')
        return time.mktime(t)
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

def get_date_str(timestamp, rollup_period='1day'):
    return date_str_functions[rollup_period](timestamp)

def get_from_to_range(date_from=None, date_to=None, duration_in_days=365):
    ts_from = ts_to = None
    if not duration_in_days:
        duration_in_days = 365
    if date_from:
        ts_from = time_round(str2time(date_form))
    if date_to:
        ts_to = min(int(time.time()), time_round(str2time(date_to)) + ONE_DAY)
    if date_from is None and date_to is None:
        ts_to = int(time.time())
        ts_from = time_round(ts_to - duration_in_days * ONE_DAY)
    if ts_from is None:
        ts_from = time_round(ts_to - duration_in_days * ONE_DAY)
    if ts_to is None:
        ts_to = min(int(time.time()), ts_from + duration_in_days * ONE_DAY)

    return ts_from, ts_to

