import simplejson

from django.forms import *
from django.utils.encoding import force_unicode
from models import TrackerModel, ViewModel
from shared.Utils import PERIOD_CHOICES, METHOD_CHOICES, TYPE_CHOICES

import re

class TrackerForm(ModelForm):
    class Meta:
        model = TrackerModel
        exclude = ('id', 'user', 'values_count', 'status')

class MultipleField(MultipleChoiceField):
    def valid_value(self, value):
        return True


class DictBasedWidget(Widget):

    def value_from_datadict(self, data, files, name):
        name_regexp = re.compile('^%s\[(\d+)\]$' % name)
        new_value = {}
        for key, value in data.iteritems():
            m = name_regexp.match(key)
            if m:
                value_id = int(m.group(1))
                new_value[value_id] = data.getlist(key)
        return simplejson.dumps(new_value)


class OptionsForm(Form):
    tracker_ids = MultipleField()
    display_values = CharField(widget=DictBasedWidget())
    period_label = 'Minimal time interval'
    help_text = """\
The minimal time interval which will be displayed on chart.
It is not recommended to select interval based on `Minute` period for the data
ranges greater than two days as there would be a lot of data to display."""
    periods = ChoiceField(label=period_label, help_text=help_text,
                          choices=PERIOD_CHOICES)
    start = DateField(label='Start', input_formats=['%d/%m/%Y'],
                      widget=TextInput(attrs={'placeholder': 'dd/mm/YYYY',
                                              'readonly': True}),
                      required=True)
    end = DateField(label='End', input_formats=['%d/%m/%Y'],
                    widget=TextInput(attrs={'placeholder': 'dd/mm/YYYY',
                                            'readonly': True}),
                    required=True)

    help_text = """\
Data aggregation method for the selected `Minimal time interval`.
We don't need aggregation method for `Minute` interval as data will be
displayed on chart as is. Other intervals requires aggregation method."""
    methods = ChoiceField(label='Aggregation Method', help_text=help_text,
                          choices=METHOD_CHOICES, required=False)
    types = ChoiceField(label='Chart Type', choices=TYPE_CHOICES, initial='line')

class ViewForm(ModelForm):
    display_values = CharField(widget=DictBasedWidget())
    start = DateField(label='Start', input_formats=['%d/%m/%Y'],
                      widget=TextInput(attrs={'placeholder': 'dd/mm/YYYY',
                                              'readonly': True}),
                      required=True)
    end = DateField(label='End', input_formats=['%d/%m/%Y'],
                    widget=TextInput(attrs={'placeholder': 'dd/mm/YYYY',
                                            'readonly': True}),
                    required=True)

    class Meta:
        model = ViewModel
        fields = ('view_name', 'view_description', 'periods', 'types',
                  'start', 'end')

    def clean(self):
        display_values = simplejson.loads(self.cleaned_data['display_values'])
        if not display_values:
            self._errors['trackers'] = 'Trackers do not exist'
        return self.cleaned_data
