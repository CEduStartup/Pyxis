import os
import re
import time
import dateutil.parser
from random import randint

ONE_MINUTE = 60
ONE_HOUR = ONE_MINUTE * 60
ONE_DAY  = ONE_HOUR * 24

PERIOD_CHOICES = (
    ('minute', 'Minute'),
    ('5minutes', '5 Minutes'),
    ('15minutes', '15 Minutes'),
    ('hour', 'Hour'),
    ('day', 'Day'),
    ('week', 'Week'),
    ('month', 'Month'),
    ('year', 'Year'),
)

METHOD_CHOICES = (
    ('avg', 'Average'),
    ('sum', 'Summed-up'),
    ('min', 'Minimal'),
    ('max', 'Maximal'),
    ('count', 'Count'),
    ('raw', 'As Is'),
)

TYPE_CHOICES = (
    ('area', 'Area'),
    ('column', 'Bar'),
    ('line', 'Line'),
)


rollup_periods = ['minute', 'hour', 'day']
rollup_periods_display = {
    'minute': '1 minute',
    'hour'  : '1 hour',
    'day'   : '1 day',
    'month' : '1 month',
}

duration_in_seconds = {
    'minute': ONE_MINUTE,
    'hour'  : ONE_HOUR,
    'day'   : ONE_DAY,
    'week'  : ONE_DAY * 7,
    'month' : ONE_DAY * 31,
}

time_formats = {
    'second': '%Y-%m-%d %H:%M:%S',
    'minute': '%Y-%m-%d %H:%M',
    'hour': '%Y-%m-%d %H',
    'day': '%Y-%m-%d',
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
    t = time.localtime(ts)
    if period == 'week':
        ts = ts - ONE_DAY * t.tm_wday
        t = time.localtime(ts)
        t = (t.tm_year, t.tm_mon, t.tm_mday, 0, 0, 0, -1, -1, -1)
    elif period == 'month':
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
        msg = '`%s` s not known time format`.' % string
        raise ValueError(msg)

def time2str(time_val, output_format='second'):
    """Convert float time value to string.

    :Parameters:
        - `time_val`: float. As returned by `time.time()`
        - `output_format`: string. One of the following: 'second', 'minute',
          'hour', 'day', 'month', or format string to pass to
          `time.strftime()`.

    :Return:
        - string with time.
    """
    if output_format in time_formats:
        output_format = time_formats[output_format]

    # TODO: I actually don't know what we need to use `localtime()` or
    # `gmtime()`.
    time_tuple = time.localtime(time_val)

    return time.strftime(output_format, time_tuple)

def get_date_str_month(ts):
    return time.strftime('%Y-%m', time.localtime(ts))

def get_date_str_week(ts):
    return time.strftime('%a %b %d', time.localtime(ts))

def get_date_str_day(ts):
    return time.strftime('%Y-%m-%d', time.localtime(ts))

def get_date_str_hour(ts):
    t = time_round(ts, 'hour')
    return time.strftime('%Y-%m-%d %H', time.localtime(t))

def get_date_str_minute(ts):
    t = time_round(ts, 'minute')
    return time.strftime('%Y-%m-%d %H:%M', time.localtime(t))

date_str_functions = {
    'minute' : get_date_str_minute,
    'hour'   : get_date_str_hour,
    'day'    : get_date_str_day,
    'week'   : get_date_str_week,
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
        pt(ts_from)
    if date_to:
        t = time.time()
        ts_to = min(int(time.time()), time_round(str2time(date_to), period) + d)
        pt(ts_to)
    if date_from is None and date_to is None:
        ts_to = int(time.time())
        ts_from = time_round(ts_to - duration, period)
    if ts_from is None:
        ts_from = time_round(ts_to - duration, period)
    if ts_to is None:
        ts_to = min(int(time.time()), ts_from + duration)

    return int(ts_from), int(ts_to)

def pt(*ts):
    """Prints timestamp in format %Y-%m-%d %H:%M"""
    if not isinstance(ts, (list, tuple)):
        ts = [ts]
    for i in ts:
        print time.strftime('%Y-%m-%d %H:%M', time.localtime(i)),
    print


def port_randomizer():
    return os.getuid() % 997

def get_base_classes(cls, include_cls=True, include_object=False):
    """Function for generating list of base classes for given class.

    :Parameters:
        - `cls`: class that list will be generated for.
        - `include_cls`: indicates whether to include cls into result list.
        - `include_object` : indicates whether to include object class into result list.

    :Return:
        - list with base classes for given.
    """
    if issubclass(object, cls):
        ret_hrc = [cls] if include_object and include_cls else []
    else:
        cur_hrc = [cls] if include_cls else []
        map(lambda base: cur_hrc.extend(get_base_classes(base, include_object=include_object)),
            cls.__bases__)
        ret_hrc = list(set(cur_hrc))
    return ret_hrc


def strip_javascript(data):
    """Function strips <script>...</script> from web page content."""
    regex = re.compile(r'<script.*?>.*?</script>', re.M|re.S)
    return regex.sub('', data)


def strip_comments(data):
    """Function strips <!--...--> from web page content."""
    regex = re.compile(r'<!--.*?-->', re.M|re.S)
    return regex.sub('', data)


def get_root_url(url):
    """Function gets root URL from given full URL."""
    regex = re.compile(r'^(.*://.*?)(?:/.*)?$')
    mo = regex.search(url)

    if mo:
        return mo.group(1)
    return ''


def replace_relative_paths(data, root_url):
    """Find relative paths in document content and replace it with given
    absolute path."""
    regex = re.compile(r'((?:src|href)="?(?=/[^/]))', re.I)
    data = regex.sub(r'\1%s' %str(root_url), data)
    return re.sub(r'url\((.*?\))', r'url(\1%s)' %str(root_url), data)
