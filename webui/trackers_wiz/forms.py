import simplejson

from shared.events.EventManager import EventSender

from django import forms
from django.forms import ModelForm
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.formtools.wizard import FormWizard
from django.shortcuts import get_object_or_404

from frontend.models import *
from shared.trackers.datasources.Errors import ResponseHTTPError, ResponseURLError, ResponseGeventTimeout
from shared.trackers.datasources.factory import get_datasource
from widgets import ValuePickerWidget

from bootstrap.forms import BootstrapModelForm, Fieldset

class TrackerNameForm(ModelForm):
    class Meta:
        model = TrackerModel
        fields = ('name', 'refresh_interval', 'status', )
        layout = (
            Fieldset('General tracker information', 'name', 'refresh_interval', 'status', ),
        )


class DataSourceForm(ModelForm):
    method_name = forms.CharField(max_length=100, required=False)
    parms = forms.CharField(max_length=100, required=False)
    URI = forms.URLField(required=True)
    class Meta:
        model = DataSourceModel
        fields = ('access_method', 'data_type')
        layout = (
            Fieldset('Specify datasources', 'access_method', 'method_name',
            'parms', 'URI', 'data_type', ),
        )

    def clean(self):
        """Method for preparing input data for storing and passing to next steps.
        """
        cleaned_data = super(DataSourceForm, self).clean()
        query = {}
        query['method_name'] = cleaned_data.get('method_name', '')
        query['parms'] = cleaned_data.get('parms', '')
        query['URI'] = cleaned_data.get('URI', '')
        cleaned_data['query'] = simplejson.dumps(query)
        try:
            datasource = get_datasource(cleaned_data)
            datasource.grab_data()
            grabbed_data = datasource.get_raw_data()
        except ResponseHTTPError:
            raise forms.ValidationError('Address "%s" cannot be opened due to server error.' % (query['URI'],))
        except ResponseURLError:
            raise forms.ValidationError('Address "%s" cannot be opened.' % (query['URI'],))
        except ResponseGeventTimeout:
            raise forms.ValidationError('Timeout on address "%s".' % (query['URI'],))
        except ValueError:
            raise forms.ValidationError('Wrong datasource configuration.')
        # Data for visualisation on next step.
        cleaned_data['grabbed_data'] = grabbed_data
        return cleaned_data

class ValueForm(ModelForm):
    extraction_rule = forms.CharField(widget=ValuePickerWidget)
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

        sender = EventSender()
        sender.fire(eid, tracker_id=tracker.id)

        return HttpResponseRedirect('/trackers/')

    def get_form(self, step=None, data=None):
        """Method that initiates form creation for current step.

        Overrided in order to add additional attributes to form's widgets.
        """
        form = super(TrackerWizard, self).get_form(step, data)
        current_step = int(step)
        if current_step == 2:
            form.fields['extraction_rule'].widget.attrs['grabbed_data'] = \
               self.initial[current_step].get('grabbed_data')
            form.fields['extraction_rule'].widget.attrs['data_type'] = \
               self.initial[current_step].get('data_type')
        return form

    def parse_params(self, request, *args, **kwargs):
        """Overrided for passing attributes to next step from validated and cleaned form.
        """
        current_step = self.determine_step(request, *args, **kwargs)
        if request.method == 'POST' and current_step == 1:
            form = self.get_form(current_step, request.POST)
            if form.is_valid():
                self.initial[(current_step + 1)]['grabbed_data'] = form.cleaned_data['grabbed_data']
                self.initial[(current_step + 1)]['data_type'] = form.cleaned_data['data_type']

