import simplejson
from forms import *
from django.shortcuts import get_object_or_404

from frontend.models import *
from trackers_wiz.forms import *

TRACKER_WIZARD_FORMS = [TrackerNameForm, DataSourceForm, ValueForm]

def add(request):
    return TrackerWizard(TRACKER_WIZARD_FORMS, initial=_make_initial_add())(request)

def _make_initial(tracker):
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
    return {
        0: {},
        1: {},
        2: {},
    }

def edit(request, tracker_id):
    tracker = get_object_or_404(TrackerModel, pk=tracker_id)
    return TrackerWizard(TRACKER_WIZARD_FORMS, initial=_make_initial(tracker))(request)

