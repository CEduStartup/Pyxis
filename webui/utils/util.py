from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import simplejson as json
from functools import wraps

def render_to(template):
    """
    Decorator for Django views that sends returned dict to render_to_response function
    with given template and RequestContext as context instance.

    If view doesn't return dict then decorator simply returns output.
    Additionally view can return two-tuple, which must contain dict as first
    element and string with template name as second. This string will
    override template name, given as parameter

    Parameters:

     - template: template name to use
    """
    def renderer(func):
        def wrapper(request, *args, **kw):
            output = func(request, *args, **kw)
            if isinstance(output, (list, tuple)):
                return render_to_response(output[1], output[0], RequestContext(request))
            elif isinstance(output, dict):
                return render_to_response(template, output, RequestContext(request))
            return output
        return wrapper
    return renderer

def render_to_json(**jsonargs):
    """
    Renders a JSON response with a given returned instance. Assumes json.dumps() can
    handle the result. The default output uses an indent of 4.

    @render_to_json()
    def a_view(request, arg1, argN):
        ...
        return {'x': range(4)}

    @render_to_json(indent=2)
    def a_view2(request):
        ...
        return [1, 2, 3]

    """
    def outer(f):
        @wraps(f)
        def inner_json(request, *args, **kwargs):
            result = f(request, *args, **kwargs)
            r = HttpResponse(mimetype='application/json')
            if result:
                indent = jsonargs.pop('indent', 4)
                r.write(json.dumps(result, indent=indent, **jsonargs))
            else:
                r.write("{}")
            return r
        return inner_json
    return outer


def singular_or_plural(singular_form, plural_form, number):
    """Return singular or plural word form depending on number."""
    if number == 1:
        return singular_form
    return plural_form


def seconds_to_time(seconds):
    """Converts number of seconds to human-readable time.

    Examples:
        1800 -> "30 minutes"
        7200 -> "2 hours"
        86400 -> "1 day"

    """
    mins, secs = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    days, hours = divmod(hours, 24)

    units = []
    if days:
        units.append('%s %s' %(days, singular_or_plural('day', 'days', days)))
    if hours:
        units.append('%s %s' %(hours, singular_or_plural('hour', 'hours', hours)))
    if mins:
        units.append('%s %s' %(mins, singular_or_plural('minute', 'minutes', mins)))
    if secs:
        units.append('%s %s' %(s, singular_or_plural('second', 'seconds', secs)))

    return ' '.join(units)
