from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.formtools.wizard import FormWizard
from django.shortcuts import get_object_or_404

from frontend.models import *

from bootstrap.forms import BootstrapModelForm, Fieldset

from shared.events.EventManager import SimpleEventSender

class TrackerNameForm(BootstrapModelForm):
    class Meta:
        model = TrackerModel
        fields = ('name', 'refresh_interval', 'status')
        layout = (
            Fieldset('General tracker information', 'name', 'refresh_interval', 'status', ),
        )


class DataSourceForm(BootstrapModelForm):
    class Meta:
        model = DataSourceModel
        fields = ('access_method', 'query', 'data_type')
        layout = (
            Fieldset('Specify datasources', 'access_method', 'query', 'data_type', ),
        )

class ValueForm(BootstrapModelForm):
    class Meta:
        model = ValueModel
        fields = ('name', 'value_type', 'extraction_rule')
        layout = (
            Fieldset('Specify values location', 'name', 'value_type', 'extraction_rule', ),
        )

class TrackerWizard(FormWizard):
    def get_template(self, step):
        return 'trackers_wiz/wizard.html'

    def done(self, request, form_list):
        tracker = None
        data_source = None
        value = None

        is_new_tracker = False

        # Handle add vs edit cases.
        if self.initial:
            edited_id = self.initial[0].get('id')
            if edited_id:
                tracker = get_object_or_404(TrackerModel, pk=edited_id)

        if not tracker:
            tracker = TrackerModel.objects.create(user=request.user)
            is_new_tracker = True
        else:
            data_source = DataSourceModel.objects.get(tracker=tracker)

        if not data_source:
            data_source = DataSourceModel.objects.create(tracker=tracker)
        else:
            value = ValueModel.objects.get(data_source=data_source)

        if not value:
            value = ValueModel.objects.create(data_source=data_source)

        value.data_source = data_source
        data_source.tracker = tracker
        # Fill in objects with new data.
        tracker.name = form_list[0].cleaned_data['name']
        tracker.refresh_interval = form_list[0].cleaned_data['refresh_interval']
        tracker.status = form_list[0].cleaned_data['status']
        data_source.access_method = form_list[1].cleaned_data['access_method']
        data_source.query = form_list[1].cleaned_data['query']
        data_source.data_type = form_list[1].cleaned_data['data_type']
        value.name = form_list[2].cleaned_data['name']
        value.value_type = form_list[2].cleaned_data['value_type']
        value.extraction_rule = form_list[2].cleaned_data['extraction_rule']
        # Save objects to database.
        tracker.save()
        data_source.save()
        value.save()

        if is_new_tracker:
            eid = 'CONFIG.TRACKER.ADDED'
        else:
            eid = 'CONFIG.TRACKER.CHANGED'

        sender = SimpleEventSender()
        sender.fire(eid, tracker_id=tracker.id)

        return HttpResponseRedirect('/trackers/')

