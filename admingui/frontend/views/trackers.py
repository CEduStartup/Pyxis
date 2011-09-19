from django.shortcuts import get_object_or_404, render_to_response
from ..forms import TrackerForm

def index(request):
    return render_to_response('frontend/trackers/index.html')

def view(request):
    return index(request)

def add(request):
    if request.method == 'POST':
        form = TrackerForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = TrackerForm()
    return render_to_response('frontend/trackers/form.html', {
        'form': form
    })

def edit(request):
    return index(request)

def enable(request):
    return index(request)
