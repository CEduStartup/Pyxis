import simplejson

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.utils.encoding import force_unicode
from frontend.models import ViewModel
from frontend.forms import OptionsForm, ViewForm
from webui.util import render_to

# TODO: Investigate if we real need it
from shared.services.services_api import mongo_storage_api, \
                                         trackers_api
from shared.Utils import METHOD_CHOICES


@login_required
@render_to('frontend/views/index.html')
def index(request):
    views = ViewModel.objects.all()
    return {'views': views}

@login_required
@render_to('frontend/trackers/view.html')
def view(request, id):
    view = ViewModel.objects.get(pk=id)

    trackers = simplejson.loads(force_unicode(view.trackers))
    # TODO: Hardcode only for ONE trackers
    tracker_id = trackers.popitem()[0]

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
    display_values = simplejson.loads(view.trackers) or {}
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
    view = None
    if id:
        view = get_object_or_404(ViewModel, pk=id)
    form = ViewForm(request.POST, instance=view)
    if form.is_valid():
        instance = form.save(commit=False)
        instance.trackers = form.cleaned_data['trackers']
        instance.save()
        response_data = {'success': True}
    else:
        response_data = {'success': False, 'errors': form.errors}

    return HttpResponse(simplejson.dumps(response_data), mimetype='application/javascript')

@login_required
def delete(request, id):
    view = ViewModel.objects.get(pk=id)
    view.delete()
    return redirect('/views/')
