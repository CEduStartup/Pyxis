import simplejson

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.utils.encoding import force_unicode
from frontend.models import AggregationModel, TrackerModel, ValueModel, ViewModel
from frontend.forms import OptionsForm, ViewForm
from utils.util import render_to

# TODO: Investigate if we real need it
from shared.services.services_api import mongo_storage_api, \
                                         trackers_api
from shared.Utils import METHOD_CHOICES


@login_required
@render_to('frontend/views/index.html')
def index(request):
    views = ViewModel.objects.filter(user=request.user)
    return {'views': views}

@login_required
@render_to('frontend/trackers/view.html')
def view(request, id):
    view = ViewModel.objects.get(pk=id)

    # TODO: Hardcode for ONE trackers
    tracker_id = view.trackers.values()[0].get('id')
    aggregations = view.aggregationmodel_set.values('max', 'min', 'avg', 'sum', 'raw', 'count')[0]

    trackers_client = trackers_api()
    tracker = trackers_client.get_trackers(tracker_id=tracker_id)[0]
    values = tracker.get_values()

    options = OptionsForm({
        'tracker_id': tracker_id,
        'periods': view.periods,
        'types': view.types,
        'start': view.start.strftime('%d/%m/%Y'),
        'end': view.end.strftime('%d/%m/%Y'),
    })

    values_id_name_list = []
    for value_id, item in values.items():
        values_id_name_list.append([value_id, item['name']])
    values_id_name_list.sort()
    values = dict(values_id_name_list)

    #TODO: Refactoring
    display_values = {str(tracker_id): []}
    for method, checked in aggregations.iteritems():
        if checked:
            display_values[str(tracker_id)].append(method)

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
            'aggregation_methods': METHOD_CHOICES, 'view': view}

@login_required
@csrf_protect
def save(request, id=None):
    view_instance = None
    if id:
        view_instance = get_object_or_404(ViewModel, pk=id)
    form = ViewForm(request.POST, instance=view_instance)
    if form.is_valid():
        #TODO: Hardcode for one tracker.
        tracker_id = form.cleaned_data['tracker_ids'][0]
        # Load trackers aggregation method from page and then delete their from
        # cleaned_data, because we dont need save it in TrackerModel
        trackers = simplejson.loads(form.cleaned_data['display_values'])
        del(form.cleaned_data['display_values'])

        view = form.save(commit=False)
        view.user = request.user
        view.save()

        # Modify aggregations tuple to default dict: {'max': False, 'min': False,...
        aggregation_default = {}
        for key, value in METHOD_CHOICES:
            aggregation_default[key] = not(bool(value))

        for value_id, methods in trackers.iteritems():
            aggregations = aggregation_default
            tracker = get_object_or_404(TrackerModel, pk=tracker_id)
            value = get_object_or_404(ValueModel, pk=value_id)
            for method in methods:
                aggregations[method] = True

            if id:
                aggr = AggregationModel.objects.filter(view=view,
                                                       tracker=tracker,
                                                       value=value)
                aggr.update(**aggregations)
            else:
                aggr = AggregationModel(view=view, tracker=tracker,
                                        value=value, **aggregations)
                aggr.save()

        response_data = {'success': True}
    else:
        response_data = {'success': False, 'errors': form.errors}

    return HttpResponse(simplejson.dumps(response_data), mimetype='application/javascript')

@login_required
def delete(request, id):
    view = ViewModel.objects.get(pk=id)
    view.delete()
    return redirect('/views/')
