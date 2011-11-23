import simplejson

from shared.events.EventManager import EventSender

from django import forms
from django.forms import ModelForm
from django.forms.util import ErrorList
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.formtools.wizard import FormWizard
from django.shortcuts import get_object_or_404

from frontend.models import *
from shared.trackers import HTTP_ACCESS_METHOD, XML_DATA_TYPE, HTML_DATA_TYPE
from shared.trackers.datasources.Errors import ResponseHTTPError, ResponseURLError, ResponseGeventTimeout
from shared.trackers.datasources.factory import get_datasource
from widgets import ValuePickerWidget

from bootstrap.forms import BootstrapModelForm, Fieldset

class TrackerNameForm(ModelForm):
    class Meta:
        model = TrackerModel
        fields = ('name', 'refresh_interval', )
        layout = (
            Fieldset('General tracker information', 'name', 'refresh_interval', ),
        )
    step_name='Tracker information'


class DataSourceForm(ModelForm):
    #method_name = forms.CharField(max_length=100, required=False)
    #parms = forms.CharField(max_length=100, required=False)
    URI = forms.URLField(required=True, label='URI:', help_text="""\
URI of your data source, like http://mypyxis.com/sample_data
""")
    class Meta:
        model = DataSourceModel
        fields = ('access_method', 'data_type', 'URI')
        layout = (
            Fieldset('Specify datasources', 'access_method',
                     'URI', 'data_type', ),
        )

    step_name = 'Data source options'

    def clean(self):
        """Method for preparing input data for storing and passing to next steps.
        """
        cleaned_data = super(DataSourceForm, self).clean()
        #Temporary check for unsupported values.
        access_method = cleaned_data.get('access_method', 0)
        data_type = cleaned_data.get('data_type', 0)
        have_errors = False
        if data_type not in (XML_DATA_TYPE,):
            self._errors['data_type'] = ('Data type not supported yet.',)
            have_errors = True
        if access_method not in (HTTP_ACCESS_METHOD,):
            self._errors['access_method'] = ('Access method not supported yet.',)
            have_errors = True
        if have_errors:
            return cleaned_data
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
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None):
        """Here we overrided constructor in order to replace field's widget.
        That was made to keep all fields attributes in models module. It isn't
        that important for syntetic fields (like URL in datasource form)
        because they aren't present in any model as is.
        """
        super(ModelForm, self).__init__(data, files, auto_id, prefix, initial,
                                        error_class, label_suffix,
                                        empty_permitted, instance)

        self.fields['extraction_rule'].widget = \
           ValuePickerWidget(attrs=self.fields['extraction_rule'].widget.attrs)

    class Meta:
        model = ValueModel
        fields = ('name', 'value_type', 'extraction_rule')
        layout = (
            Fieldset('Specify values location', 'name', 'value_type', 'extraction_rule', ),
        )
    step_name = 'Tracked value setup'

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
        tracker.status = 1
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

        # Clean temporary data.
        del request.session['extra_cleaned_data']

        return HttpResponseRedirect('/trackers/')

    def get_form(self, step=None, data=None):
        """Method that initiates form creation for current step.

        Overrided in order to add additional attributes to form's widgets.
        """
        form = super(TrackerWizard, self).get_form(step, data)
        current_step = int(step)
        if current_step == 2:
            form.fields['extraction_rule'].widget.attrs['grabbed_data'] = \
               self.extra_cleaned_data.get('grabbed_data')
            form.fields['extraction_rule'].widget.attrs['data_type'] = \
               self.extra_cleaned_data.get('data_type')
        return form

    def parse_params(self, request, *args, **kwargs):
        """Overrided for passing attributes to next step from validated and cleaned form.
        """
        current_step = self.determine_step(request, *args, **kwargs)
        self.extra_cleaned_data = request.session.get('extra_cleaned_data', {})
        if request.method == 'POST' and current_step == 1:
            form = self.get_form(current_step, request.POST)
            if form.is_valid():
                self.extra_cleaned_data['grabbed_data'] = form.cleaned_data['grabbed_data']
                self.extra_cleaned_data['data_type'] = form.cleaned_data['data_type']
                request.session['extra_cleaned_data'] = self.extra_cleaned_data

