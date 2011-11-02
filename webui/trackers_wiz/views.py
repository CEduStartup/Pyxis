import simplejson
from forms import *
from django.shortcuts import get_object_or_404

from frontend.models import *
from trackers_wiz.forms import *

TRACKER_WIZARD_FORMS = [TrackerNameForm, DataSourceForm, ValueForm]

def add(request):
    return TrackerWizard(TRACKER_WIZARD_FORMS)(request)

def _make_initial(tracker):
    data_source = DataSourceModel.objects.get(tracker=tracker)
    value = ValueModel.objects.get(data_source=data_source)

    method_name = ''
    parms = ''
    uri = ''
    try:
        query = simplejson.loads(data_source.query)
        method_name = query['method_name']
        parms = query['parms']
        uri = query['uri']
    except simplejson.decoder.JSONDecodeError:
        print 'Can not load json object'
    finally:
        return {
             0: {'name': tracker.name, 'id': tracker.id,
                 'status': tracker.status,
                 'refresh_interval': tracker.refresh_interval},
             1: {'data_type': data_source.data_type, 'parms': parms,
                 'method_name': method_name, 'uri': uri,
                 'access_method': data_source.access_method},
             2: {'value_type': value.value_type , 'name': value.name,
                 'extraction_rule': value.extraction_rule},
           }

def edit(request, tracker_id):
    tracker = get_object_or_404(TrackerModel, pk=tracker_id)
    return TrackerWizard(TRACKER_WIZARD_FORMS, initial=_make_initial(tracker))(request)

