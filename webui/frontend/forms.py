from django.forms import *
from models import TrackerModel

class TrackerForm(ModelForm):
    class Meta:
        model = TrackerModel
        exclude = ('id', 'user', 'values_count', 'status')

class OptionsForm(Form):

    PERIOD_CHOICES = (
        ('hour', 'Hour'),
        ('day', 'Day'),
        ('week', 'Week'),
        ('month', 'Month'),
        ('year', 'Year'),
    )

    METHOD_CHOICES = (
        ('avg', 'AVG'),
        ('summ', 'SUMM'),
        ('min', 'MIN'),
        ('max', 'MAX'),
    )

    TYPE_CHOICES = (
        ('area', 'Area'),
        ('column', 'Bar'),
        ('line', 'Line'),
    )

    id = IntegerField(widget=HiddenInput())
    periods = ChoiceField(label='Period', choices=PERIOD_CHOICES)
    start = DateField(label='Start', input_formats='%d/%m/%Y',
                      widget=TextInput(attrs=
                         {'placeholder': 'dd/mm/YYYY'}))
    end = DateField(label='End', input_formats='%d/%m/%Y',
                    widget=TextInput(attrs=
                       {'placeholder': 'dd/mm/YYYY'}))
    methods = ChoiceField(label='Method', choices=METHOD_CHOICES)
    types = ChoiceField(label='Type', choices=TYPE_CHOICES, initial='column')
