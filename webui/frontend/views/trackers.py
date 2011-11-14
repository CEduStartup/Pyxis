import bjsonrpc
import simplejson

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.utils.encoding import force_unicode
from frontend.models import TrackerModel, ViewModel
from frontend.forms import OptionsForm, TrackerForm, ViewForm
from webui.util import render_to

from datetime import date, timedelta
from shared.services.services_api import mongo_storage_api, \
                                         trackers_api
from shared.Utils import METHOD_CHOICES
from pprint import pprint as pp

aggr_map = dict(METHOD_CHOICES)


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
def view(request, tracker_id=None):
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
    tracker_ids = [tracker_id]

    trackers_client = trackers_api()
    tracker = trackers_client.get_trackers(tracker_id=tracker_id)[0]
    values = tracker.get_values()
    values_id_name_list = []
    for value_id, item in values.items():
        values_id_name_list.append([value_id, item['name']])
    values_id_name_list.sort()
    values = dict(values_id_name_list)
    display_values = {}
    default_aggr = 'avg'
    if options.data['periods'] == 'minute':
        default_aggr = 'raw'
    if not display_values:
        for value_id in values:
            display_values[str(value_id)] = [default_aggr]
    for row in values_id_name_list:
        value_id = str(row[0])
        row.append(display_values.get(value_id, []))
    return {'tracker': tracker, 'options': options,
            'tracker_values': values_id_name_list,
            'aggregation_methods': METHOD_CHOICES}

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

@login_required
def get_data_to_display(request):
    trackers_client = trackers_api()
    mongo_client = mongo_storage_api()
    options = OptionsForm(request.POST)
    options.is_valid()
    start = options.cleaned_data['start'].strftime('%Y-%m-%d')
    end = options.cleaned_data['end'].strftime('%Y-%m-%d')
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
    default_aggr = 'avg'
    if options.data['periods'] == 'minute':
        default_aggr = 'raw'

    display_values = options.cleaned_data['display_values']
    display_values = simplejson.loads(force_unicode(display_values))

    default_aggr = 'avg'
    if options.data['periods'] == 'minute':
        default_aggr = 'raw'

    data_list = []
    tracker_ids = options.cleaned_data['tracker_ids']
    for tracker_id in tracker_ids:
        try:
            tracker = trackers_client.get_trackers(tracker_id=tracker_id)[0]
        except IndexError:
            continue
        values = tracker.get_values()
        values_id_name_list = []
        for value_id, item in values.items():
            values_id_name_list.append([value_id, item['name']])
        values_id_name_list.sort()
        values = dict(values_id_name_list)
        print 'test: ', values
        if not display_values:
            for value_id in values:
                display_values[str(value_id)] = [default_aggr]
        for row in values_id_name_list:
            value_id = str(row[0])
            row.append(display_values.get(value_id, []))
        src_parms = []
        print display_values
        for value_id, methods in display_values.iteritems():
            for aggr in methods:
                src_parms.append((value_id, aggr))
        if not display_values:
            for value_id in values:
                display_values[str(value_id)] = [default_aggr]
        for row in values_id_name_list:
            value_id = str(row[0])
            row.append(display_values.get(value_id, []))
        src_parms = []
        for value_id, methods in display_values.iteritems():
            for aggr in methods:
                src_parms.append((value_id, aggr))

        data = mongo_client.get_tracker_data(int(tracker_id), period, src_parms,
                                             date_from=start, date_to=end,
                                             periods_in_group=periods_in_group)
        for row in data:
            value_id, aggr = row['name']
            value_name = values[value_id]
            aggr_method = aggr_map.get(aggr, '')
            row['name'] = '%s Value for %s' % (aggr_method, value_name)
        data_list.extend(data)
    return HttpResponse(simplejson.dumps(data_list), mimetype='application/javascript')
