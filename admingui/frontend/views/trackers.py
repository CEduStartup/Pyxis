from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.views.generic.simple import redirect_to
from django.contrib.auth.decorators import login_required
from ..models import Tracker
from ..forms import TrackerForm
from admingui.util import render_to
import admingui

@login_required
@render_to('frontend/trackers/index.html')
def index(request):
    trackers = Tracker.objects.all()
    return locals()

@login_required
@render_to('frontend/trackers/view.html')
def view(request, tracker_id):
    tracker = get_object_or_404(Tracker, pk=tracker_id, user=request.user)
    return locals()

@login_required
def add(request):
    return form(request, Tracker(user=request.user))

@login_required
def edit(request, tracker_id):
    return form(request, get_object_or_404(Tracker, pk=tracker_id, user=request.user))
    
@render_to('frontend/trackers/form.html')
def form(request, tracker):
    if request.method == 'POST':
        form = TrackerForm(request.POST, instance=tracker)
        if form.is_valid():
            form.save()
            return redirect('/trackers/index/')
    else:
        form = TrackerForm(instance=tracker)
    tracker_id = tracker.id
    return locals()

@login_required
def enable(request):
    return index(request)
