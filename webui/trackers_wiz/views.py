import simplejson
from forms import *
import urllib2
import re
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from frontend.models import *
from trackers_wiz.forms import *

from shared.Parser import get_parser, ParserCastError, ParserError
from shared.trackers import VALUE_TYPES
from shared.Utils import strip_javascript, strip_comments, get_root_url, \
                         replace_relative_paths

from lxml.etree import XPathEvalError

TEST_STATUS_OK = 0
TEST_STATUS_XPATH_ERROR = -1
TEST_STATUS_CAST_ERROR = -2

TRACKER_WIZARD_FORMS = [TrackerNameForm, DataSourceForm, ValueForm]

def add(request):
    return TrackerWizard(TRACKER_WIZARD_FORMS, initial=_make_initial_add())(request)

def _make_initial(tracker):
    """Creates wizard's initial dict for edit action.
    """
    data_source = DataSourceModel.objects.get(tracker=tracker)
    value = ValueModel.objects.get(data_source=data_source)

    query = {}
    try:
        query = simplejson.loads(data_source.query)
    except simplejson.decoder.JSONDecodeError:
        print 'Can not load json object'

    method_name = query.get('method_name', '')
    parms = query.get('parms', '')
    URI = query.get('URI', '')

    return {
         0: {'name': tracker.name, 'id': tracker.id,
             'status': tracker.status,
             'refresh_interval': tracker.refresh_interval},
         1: {'data_type': data_source.data_type, 'parms': parms,
             'method_name': method_name, 'URI': URI,
             'access_method': data_source.access_method},
         2: {'value_type': value.value_type , 'name': value.name,
             'extraction_rule': value.extraction_rule},
       }

def _make_initial_add():
    """Creates wizard's initial dict for add action.

    We need to create such dict because by default wizard creates empty dict
    while we need dict with steps keys for processing.
    """
    return {
        0: {},
        1: {},
        2: {},
    }

def edit(request, tracker_id):
    tracker = get_object_or_404(TrackerModel, pk=tracker_id)
    return TrackerWizard(TRACKER_WIZARD_FORMS, initial=_make_initial(tracker))(request)


def get_url(request, URL):
    """Method gets retrieves data from given URL and passes it to template."""
    url_request = urllib2.Request(URL)
    url_request.add_header('User-agent', 'Mozilla/5.0')
    response = urllib2.urlopen(url_request)
    data = strip_javascript(response.read())
    data = strip_comments(data)
    data = replace_relative_paths(data, get_root_url(URL))
    return HttpResponse(data, mimetype='text/html')


@csrf_exempt
def try_xpath(request):
    status = TEST_STATUS_OK
    data = ''
    # TODO: we have a constants for these in shared/trackers/datasources
    form = ValueForm(request.GET)
    if form.is_valid():
        # TODO: We can try to create Tracker or at least datasource object
        # to fetch data.
        URL = request.session['extra_cleaned_data']['URI']
        url_request = urllib2.Request(URL)
        url_request.add_header('User-agent', 'Mozilla/5.0')
        response = urllib2.urlopen(url_request)
        data = response.read()
        data = strip_javascript(data)
        data = strip_comments(data)
        data = replace_relative_paths(data, get_root_url(URL))
        value_type = form.cleaned_data['value_type']
        data_type = request.session['extra_cleaned_data']['data_type']
        parser = get_parser(data_type, gevent_safe=False)
        parser.initialize()
        parser.parse(data)
        try:
            data = parser.get_value(form.cleaned_data['extraction_rule'],
                                    value_type=value_type)
            data = 'Data successfully extracted: %s' % (data[0],)
            status = TEST_STATUS_OK
        except ParserCastError, err:
            status = TEST_STATUS_CAST_ERROR
            data = str(err)
        except ParserError:
            status = TEST_STATUS_XPATH_ERROR
            data = 'Node Extraction Failed, try top correct extraction rule manually !'
        except Exception:
            # TODO: errors handling
            import traceback as tb
            data = tb.format_exc()
        finally:
            return HttpResponse(simplejson.dumps({'status': status,
                                                  'data': data}),
                                                  mimetype='application/json')

    else:
        return HttpResponse('Please set extraction rule', mimetype='text/html')

