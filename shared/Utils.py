import time
import dateutil.parser
from random import randint

ONE_MIN = 60
ONE_HOUR = ONE_MIN * 60
ONE_DAY  = ONE_HOUR * 24

rollup_periods = ['minute', 'hour', 'day']
rollup_periods_display = {
    'minute': '1 minute',
    'hour'  : '1 hour',
    'day'   : '1 day',
    'month' : '1 month',
}

duration_in_seconds = {
    'minute'  : ONE_MIN,
    'hour' : ONE_HOUR,
    'day'  : ONE_DAY,
    'month': ONE_DAY * 31,
}

time_formats = {
    'minute'  : '%Y-%m-%d %H:%M',
    'hour' : '%Y-%m-%d %H',
    'day'  : '%Y-%m-%d',
    'month': '%Y-%m',
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

def time_round(ts, period='day'):
    t = time.gmtime(ts)
    if period == 'month':
        t = (t.tm_year, t.tm_mon, 1, 0, 0, 0, -1, -1, -1)
    elif period == 'day':
        t = (t.tm_year, t.tm_mon, t.tm_mday, 0, 0, 0, -1, -1, -1)
    elif period == 'hour':
        t = (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, 0, 0, -1, -1, -1)
    elif period == 'minute':
        t = (t.tm_year, t.tm_mon, t.tm_mday, t.tm_hour, t.tm_min, 0, -1, -1, -1)
    else:
        msg = """\
`period` must be `month`, `day`, `hour` or `minute` (got %s)""" % \
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

def get_date_str_month(ts):
    return time.strftime('%Y-%m', time.gmtime(ts))

def get_date_str_day(ts):
    return time.strftime('%Y-%m-%d', time.gmtime(ts))

def get_date_str_hour(ts):
    t = time_round(ts, 'hour')
    return time.strftime('%Y-%m-%d %H', time.gmtime(t))

def get_date_str_minute(ts):
    t = time_round(ts, 'minute')
    return time.strftime('%Y-%m-%d %H:%M', time.gmtime(t))

date_str_functions = {
    'minute' : get_date_str_minute,
    'hour'   : get_date_str_hour,
    'day'    : get_date_str_day,
    'month'  : get_date_str_month,
}

def get_date_str(timestamp, period='day'):
    try:
        timestamp = int(timestamp)
    except ValueError:
        timestamp = str2time(timestamp)
    return date_str_functions[period](timestamp)

def get_from_to_range(date_from=None, date_to=None, period='day',
                      periods_count=365):
    ts_from = ts_to = None
    d = duration_in_seconds[period]
    if not periods_count:
        periods_count = 365
    duration = d * periods_count
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

