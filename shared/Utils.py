import time
import dateutil.parser
from random import randint

ONE_MIN = 60
ONE_HOUR = ONE_MIN * 60
ONE_DAY  = ONE_HOUR * 24

rollup_periods = ['1min', '1hour', '1day', '1month']
rollup_periods_display = {
    '1min'  : '5 minutes',
    '1hour' : '1 hour',
    '1day'  : '1 day',
    '1month': '1 month',
}

duration_in_seconds = {
    '1min'  : ONE_MIN,
    '1hour' : ONE_HOUR,
    '1day'  : ONE_DAY,
    '1month': ONE_DAY * 31,
}

time_formats = {
    '1min'  : '%Y-%m-%d %H:%M',
    '1hour' : '%Y-%m-%d %H',
    '1day'  : '%Y-%m-%d',
    '1month': '%Y-%m',
}

def value_generator(n):
    while 1:
        f = n - randint(0, 15)
        if f < -30:
            f = -30
        t = n + randint(0, 15)
        if t > 50:
            t = 50
        n = randint(f, t)
        yield n

def time_round(ts, period='1day'):
    t = time.localtime(ts)
    if period == '1month':
        t = (t.tm_year, t.tm_mon, 1, 0, 0, 0, -1, -1, -1)
    elif period == '1day':
        t = (t.tm_year, t.tm_mon, t.tm_mday, 0, 0, 0, -1, -1, -1)
    elif period == '1hour':
        t = (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, 0, 0, -1, -1, -1)
    elif period == '1min':
        t = (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, 0, -1, -1, -1)
    else:
        msg = """\
`period` must be `1month`, `1day`, `1hour` or `1min` (got %s)""" % \
            (period,)
        raise ValueError(msg)

    return int(time.mktime(t))

def str2time(string):
    try:
        d = dateutil.parser.parse(string)
        return time.mktime(d.timetuple())
    except:
        msg = '`%s` s not known time format`.'
        raise ValueError(msg)

def get_date_str_1month(ts):
    return time.strftime('%Y-%m', time.localtime(ts))

def get_date_str_1day(ts):
    return time.strftime('%Y-%m-%d', time.localtime(ts))

def get_date_str_1hour(ts):
    t = time_round(ts, '1hour')
    return time.strftime('%Y-%m-%d %H', time.localtime(t))

def get_date_str_1min(ts):
    t = time_round(ts, '1min')
    return time.strftime('%Y-%m-%d %H:%M', time.localtime(t))

date_str_functions = {
    '1min'    : get_date_str_1min,
    '1hour'   : get_date_str_1hour,
    '1day'    : get_date_str_1day,
    '1month'  : get_date_str_1month,
}

def get_date_str(timestamp, period='1day'):
    try:
        timestamp = int(timestamp)
    except ValueError:
        timestamp = str2time(timestamp)
    return date_str_functions[period](timestamp)

def get_from_to_range(date_from=None, date_to=None, period='1day',
                      periods_count=365):
    ts_from = ts_to = None
    d = duration_in_seconds[period]
    if not periods_count:
        periods_count = 365
    if date_from:
        ts_from = time_round(str2time(date_from), period)
    if date_to:
        ts_to = min(int(time.time()), time_round(str2time(date_to), period) + d)
    if date_from is None and date_to is None:
        ts_to = int(time.time())
        ts_from = time_round(ts_to - duration, period)
    if ts_from is None:
        ts_from = time_round(ts_to - duration, period)
    if ts_to is None:
        ts_to = min(int(time.time()), ts_from + duration)

    return int(ts_from), int(ts_to)

