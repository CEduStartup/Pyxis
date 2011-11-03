import bjsonrpc
import simplejson

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.views.decorators.csrf import csrf_protect
from django.utils.encoding import force_unicode
from frontend.models import TrackerModel
from frontend.forms import OptionsForm, TrackerForm
from webui.util import render_to

from datetime import date, timedelta
from shared.services.services_api import mongo_storage_api, \
                                         trackers_api
from pprint import pprint as pp

aggregation_methods = (
    ('min', 'Minimal'),
    ('max', 'Maximal'),
    ('avg', 'Average'),
    ('sum', 'Summed up'),
    ('count', 'Count'),
    ('raw', 'As Is'),
)
aggr_map = dict(aggregation_methods)


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
        options.is_valid()
        tracker_id = options.cleaned_data['tracker_id']
        start = options.cleaned_data['start'].strftime('%Y-%m-%d')
        end = options.cleaned_data['end'].strftime('%Y-%m-%d')
    else:
        today = date.today()
        yesterday = today - timedelta(days=1)
        options = OptionsForm({
            'tracker_id': tracker_id,
            'periods': 'hour',
            'types': 'line',
            'start': yesterday.strftime('%d/%m/%Y'),
            'end': today.strftime('%d/%m/%Y'),
        })
        start = yesterday.strftime('%Y-%m-%d')
        end = today.strftime('%Y-%m-%d')
    period = options.data['periods']
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

    trackers_client = trackers_api()
    tracker_config = trackers_client.get_trackers(tracker_id=tracker_id)
    tracker_model = get_object_or_404(TrackerModel, pk=tracker_id,
                                      #user=request.user
    )
    values = {}
    for tracker in tracker_config:
        values.update(tracker.get_values())
    values_id_name_list = []
    for value_id, item in values.items():
        values_id_name_list.append([value_id, item['name']])
    values_id_name_list.sort()
    values = dict(values_id_name_list)
    if request.POST:
        display_values = options.cleaned_data['display_values']
        display_values = simplejson.loads(force_unicode(display_values))
    else:
        display_values = {}
        for value_id in values:
            display_values[str(value_id)] = ['avg', 'raw']
    for row in values_id_name_list:
        value_id = str(row[0])
        row.append(display_values.get(value_id, []))
    src_parms = []
    for value_id, methods in display_values.iteritems():
        for aggr in methods:
            src_parms.append((value_id, aggr))

    mongo_client = mongo_storage_api()
    data = mongo_client.get_tracker_data(int(tracker_id), period, src_parms,
                                         date_from=start, date_to=end,
                                         periods_in_group=periods_in_group)
    for row in data:
        value_id, aggr = row['name']
        value_name = values[value_id]
        aggr_method = aggr_map.get(aggr, '')
        row['name'] = '%s Value for %s' % (aggr_method, value_name)
    tracker_model.data = simplejson.dumps(data)
    return {'tracker': tracker_model, 'options': options,
            'tracker_values': values_id_name_list,
            'aggregation_methods': aggregation_methods}

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
