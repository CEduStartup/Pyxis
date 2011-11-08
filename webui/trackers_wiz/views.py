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
    return {
	     0: {'name': tracker.name, 'id': tracker.id, 'status': tracker.status, 'refresh_interval': tracker.refresh_interval},
	     1: {'data_type': data_source.data_type, 'access_method': data_source.access_method, 'query': data_source.query},
	     2: {'value_type': value.value_type, 'extraction_rule': value.extraction_rule, 'name': value.name},
	   }

def edit(request, tracker_id):
    tracker = get_object_or_404(TrackerModel, pk=tracker_id)
    return TrackerWizard(TRACKER_WIZARD_FORMS, initial=_make_initial(tracker))(request)

    
