import bjsonrpc
import simplejson

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_protect
from frontend.models import TrackerModel
from frontend.forms import OptionsForm, TrackerForm
from webui.util import render_to

from datetime import date, timedelta
from pprint import pprint as pp

@login_required
@render_to('frontend/trackers/index.html')
def index(request):
    trackers = TrackerModel.objects.all()
    return locals()

@login_required
@render_to('frontend/trackers/index.html')
def private_trackers(request):
    # List of private trackers.
    trackers = TrackerModel.objects.all()
    return locals()

@login_required
@render_to('frontend/trackers/view.html')
def view(request, tracker_id):
    if request.POST:
        options = OptionsForm(request.POST)
        tracker_id = options.data['tracker_id'][0]
    else:
        today = date.today()
        yesterday = today - timedelta(days=1)
        print yesterday, today
        options = OptionsForm({
            'tracker_id': tracker_id,
            'periods': 'hour',
            'types': 'line',
            'start': yesterday.strftime('%d/%m/%Y'),
            'end': today.strftime('%d/%m/%Y'),
        })
    print options.data
    period = options.data['periods']
    print '------------', period
    periods_in_group = 1
    if period == '5minutes':
        period = 'minute'
        periods_in_group = 5
    elif period == '15minutes':
        period = 'minute'
        periods_in_group = 15
    elif period == 'year':
        period = 'month'
        periods_in_group = 12
    tmp = []
    start = options.data['start']
    end = options.data['end']
    for d in (start, end):
        t = d.split('/')
        tmp.append('-'.join([t[2], t[1], t[0]]))
    start, end = tmp
    print period
    tracker = get_object_or_404(TrackerModel, pk=tracker_id,
                                #user=request.user
                                )
    c = bjsonrpc.connect(settings.RPC_HOST, settings.RPC_PORT)
    data = c.call.get_tracker_data(int(tracker_id), period, date_from=start,
              date_to=end, periods_in_group=periods_in_group)
    tracker.data = simplejson.dumps(data)
    return {'tracker': tracker, 'options': options}

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
