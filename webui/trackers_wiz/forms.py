import simplejson

from shared.events.EventManager import EventSender

from django import forms
from django.db import transaction
from django.forms import ModelForm
from django.forms.util import ErrorList
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.formtools.wizard import FormWizard
from django.shortcuts import get_object_or_404

from frontend.models import *
from shared.events.Event import NewTrackerAddedEvent, TrackerConfigChangedEvent
from shared.Parser import get_parser, ParserSyntaxError
from shared.trackers import HTTP_ACCESS_METHOD, XML_DATA_TYPE, HTML_DATA_TYPE
from shared.trackers.datasources.Errors import ResponseHTTPError, ResponseURLError, ResponseGeventTimeout
from shared.trackers.datasources.factory import get_datasource
from webui.frontend.models import ValueModel, DataSourceModel, TrackerModel
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
        access_method = cleaned_data.get('access_method', 0)
        data_type = cleaned_data.get('data_type', 0)
        have_errors = False

        # Temporary check for unsupported values.
        if data_type not in (XML_DATA_TYPE, HTML_DATA_TYPE,):
            self._errors['data_type'] = ('Data type is not supported yet.',)
            have_errors = True
        if access_method not in (HTTP_ACCESS_METHOD,):
            self._errors['access_method'] = ('Access method is not supported yet.',)
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
            parser = get_parser(data_type, gevent_safe=False)
            parser.initialize()
            parser.parse(grabbed_data)

        except ResponseHTTPError:
            raise forms.ValidationError('Address "%s" cannot be opened due to server error.' % (query['URI'],))
        except ResponseURLError:
            raise forms.ValidationError('Address "%s" cannot be opened.' % (query['URI'],))
        except ResponseGeventTimeout:
            raise forms.ValidationError('Timeout on address "%s".' % (query['URI'],))
        except ParserSyntaxError:
            raise forms.ValidationError('Data source returns malformed document or data type is wrong.')
        except ValueError:
            raise forms.ValidationError('Wrong datasource configuration.')
        # Data for visualisation on next step.

        cleaned_data['grabbed_data'] = parser
        cleaned_data['raw_data'] = grabbed_data
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

    @transaction.commit_on_success
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

        if len(form_list):
            tracker.name = form_list[0].cleaned_data['name']
            tracker.refresh_interval = form_list[0].cleaned_data['refresh_interval']
            tracker.status = 1
            tracker.save()

        if len(form_list) == 2:
            data_source.access_method = form_list[1].cleaned_data['access_method']
            data_source.query = form_list[1].cleaned_data['query']
            data_source.data_type = form_list[1].cleaned_data['data_type']
            data_source.save()

        if len(form_list) == 3:
            value.name = form_list[2].cleaned_data['name']
            value.value_type = form_list[2].cleaned_data['value_type']
            value.extraction_rule = form_list[2].cleaned_data['extraction_rule']
            value.save()

        if is_new_tracker:
            event_cls = NewTrackerAddedEvent
        else:
            event_cls = TrackerConfigChangedEvent

        sender = EventSender()
        sender.fire(event_cls, tracker_id=tracker.id)

        # Clean temporary data.
        if 'extra_cleaned_data' in request.session:
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
            form.fields['extraction_rule'].widget.attrs['URI'] = \
               self.extra_cleaned_data.get('URI')
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
                self.extra_cleaned_data['URI'] = form.cleaned_data['URI']
                request.session['extra_cleaned_data'] = self.extra_cleaned_data

    def __call__(self, request, *args, **kwargs):
        """
        Main method that does all the hard work, conforming to the Django view
        interface.
        """
        if 'extra_context' in kwargs:
            self.extra_context.update(kwargs['extra_context'])
        current_step = self.determine_step(request, *args, **kwargs)
        self.parse_params(request, *args, **kwargs)

        # Sanity check.
        if current_step >= self.num_steps():
            raise Http404('Step %s does not exist' % current_step)

        # Validate and process all the previous forms before instantiating the
        # current step's form in case self.process_step makes changes to
        # self.form_list.

        # If any of them fails validation, that must mean the validator relied
        # on some other input, such as an external Web site.

        # It is also possible that alidation might fail under certain attack
        # situations: an attacker might be able to bypass previous stages, and
        # generate correct security hashes for all the skipped stages by virtue
        # of:
        #  1) having filled out an identical form which doesn't have the
        #     validation (and does something different at the end),
        #  2) or having filled out a previous version of the same form which
        #     had some validation missing,
        #  3) or previously having filled out the form when they had more
        #     privileges than they do now.
        #
        # Since the hashes only take into account values, and not other other
        # validation the form might do, we must re-do validation now for
        # security reasons.
        previous_form_list = []
        for i in range(current_step):
            f = self.get_form(i, request.POST)
            if not self._check_security_hash(request.POST.get("hash_%d" % i, ''),
                request, f):
                return self.render_hash_failure(request, i)

            if not f.is_valid():
                return self.render_revalidation_failure(request, i, f)
            else:
                self.process_step(request, f, i)
                previous_form_list.append(f)

        # Process the current step. If it's valid, gorender_to_response to the next step or call
        # done(), depending on whether any steps remain.
        if request.method == 'POST':
            form = self.get_form(current_step, request.POST)
        else:
            form = self.get_form(current_step)

        if form.is_valid():
            self.process_step(request, form, current_step)

            if form.data['control'] == 'Next':
                next_step = current_step + 1
            else:
                next_step = current_step - 1

            if form.data['control'] == 'Done' or next_step == self.num_steps():
                return self.done(request, previous_form_list + [form])
            else:
                form = self.get_form(next_step)
                self.step = current_step = next_step

        return self.render(form, request, current_step)

