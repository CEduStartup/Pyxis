from django.forms import *
from models import TrackerModel

class TrackerForm(ModelForm):
    class Meta:
        model = TrackerModel
        exclude = ('id', 'user', 'values_count', 'status')

class OptionsForm(Form):

    PERIOD_CHOICES = (
        ('minute', 'Minute'),
        ('5minutes', '5 Minutes'),
        ('15minutes', '15 Minutes'),
        ('hour', 'Hour'),
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('year', 'Year'),
    )

    METHOD_CHOICES = (
        ('avg', 'Average Value'),
        ('sum', 'Summed-up Value'),
        ('min', 'Minimal Value'),
        ('max', 'Maximal Value'),
        ('count', 'Count'),
    )

    TYPE_CHOICES = (
        ('area', 'Area'),
        ('column', 'Bar'),
        ('line', 'Line'),
    )

    tracker_id = IntegerField(widget=HiddenInput())
    period_label = 'Minimal time interval'
    help_text = """\
The minimal time interval which will be displayed on chart.
It is not recommended to select interval based on `Minute` period for the data
ranges greater than two days as there would be a lot of data to display."""
    periods = ChoiceField(label=period_label, help_text=help_text,
                          choices=PERIOD_CHOICES)
    start = DateField(label='Start', input_formats=['%d/%m/%Y'],
                      widget=TextInput(attrs={'placeholder': 'dd/mm/YYYY'}),
                      required=False)
    end = DateField(label='End', input_formats=['%d/%m/%Y'],
                    widget=TextInput(attrs={'placeholder': 'dd/mm/YYYY'}),
                    required=False)

    help_text = """\
Data aggregation method for the selected `Minimal time interval`.
We don't need aggregation method for `Minute` interval as data will be
displayed on chart as is. Other intervals requires aggregation method."""
    methods = ChoiceField(label='Aggregation Method', help_text=help_text,
                          choices=METHOD_CHOICES, required=False)
    types = ChoiceField(label='Type', choices=TYPE_CHOICES, initial='line')
