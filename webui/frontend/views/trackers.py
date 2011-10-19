import bjsonrpc
import simplejson

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from ..models import Tracker
from ..forms import OptionsForm, TrackerForm
from webui.util import render_to

from pprint import pprint as pp

@login_required
@render_to('frontend/trackers/index.html')
def index(request):
    trackers = Tracker.objects.all()
    return locals()

@login_required
@render_to('frontend/trackers/view.html')
def view(request, tracker_id):
    options = OptionsForm()
    options['id'].value = tracker_id
    tracker = get_object_or_404(Tracker, pk=tracker_id,
                                #user=request.user
                                )
    c = bjsonrpc.connect(settings.RPC_HOST, settings.RPC_PORT)
    data = c.call.get_tracker_data(1)
    tracker.data = simplejson.dumps(data)
    return {'tracker': tracker, 'options': options}

@login_required
def add(request):
    return form(request, Tracker(
                                 #user=request.user
                                 ))

@login_required
def edit(request, tracker_id):
    return form(request, get_object_or_404(Tracker, pk=tracker_id,
                                           #user=request.user
                                           ))

@csrf_protect
@render_to('frontend/trackers/form.html')
def form(request, tracker):
    form = TrackerForm(request.POST or None, instance=tracker)
    if form.is_valid():
        form.save()
        return redirect('/trackers/index/')
    tracker_id = tracker.id
    return locals()

@login_required
def enable(request):
    return index(request)
