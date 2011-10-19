from forms import *
from django.shortcuts import get_object_or_404

from frontend.models import TrackerModel

TRACKER_WIZARD_FORMS = [TrackerGeneral, TrackerFormat, TrackerPath, TrackerPollInterval, TrackerPrivacy]

def add(request):
    return TrackerWizard(TRACKER_WIZARD_FORMS)(request)

def _make_initial(tracker):
    return {
	     0: {'name': tracker.name, 'url': tracker.url, 'id': tracker.id},
	     1: {'data_type': tracker.data_type},
	     2: {'path': tracker.path, 'value_name': tracker.value_name},
	     3: {'interval': tracker.interval, 'interval_kind': tracker.interval_kind},
	     4: {'privacy': tracker.privacy}
	   }

def edit(request, tracker_id):
    tracker = get_object_or_404(TrackerModel, pk=tracker_id)
    return TrackerWizard(TRACKER_WIZARD_FORMS, initial=_make_initial(tracker))(request)

    
