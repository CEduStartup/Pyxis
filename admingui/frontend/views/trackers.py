from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.views.generic.simple import redirect_to
from django.contrib.auth.decorators import login_required
from ..models import Tracker
from ..forms import TrackerForm

@login_required
def index(request):
    trackers = Tracker.objects.all()
    return render_to_response('frontend/trackers/index.html', {
        'trackers': trackers
    })

@login_required
def view(request, tracker_id):
    return index(request)

@login_required
def add(request):
    return form(request, Tracker(user=request.user))

@login_required
def edit(request, tracker_id):
    return form(request, get_object_or_404(Tracker, pk=tracker_id, user=request.user))
    
def form(request, tracker):
    if request.method == 'POST':
        form = TrackerForm(request.POST, instance=tracker)
        if form.is_valid():
            form.save()
            return redirect('/trackers/index/')
    else:
        form = TrackerForm(instance=tracker)
    return render_to_response('frontend/trackers/form.html', {
        'form': form
    })        

@login_required
def enable(request):
    return index(request)
