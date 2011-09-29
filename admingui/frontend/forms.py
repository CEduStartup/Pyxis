import django.forms

from django import forms
from models import Tracker

class TrackerForm(forms.ModelForm):
    class Meta:
        model = Tracker
        exclude = ('id', 'user', 'values_count', 'status')

class OptionsForm(forms.Form):

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
        ('bar', 'Bar'),
        ('line', 'Line'),
    )

    periods = forms.ChoiceField(label='Period', choices=PERIOD_CHOICES)
    start = forms.DateField(label='Start', input_formats='%d/%m/%Y',
                            widget=forms.TextInput(attrs=
                               {'placeholder': 'dd/mm/YYYY'}))
    end = forms.DateField(label='End', input_formats='%d/%m/%Y',
                          widget=forms.TextInput(attrs=
                             {'placeholder': 'dd/mm/YYYY'}))
    methods = forms.ChoiceField(label='Method', choices=METHOD_CHOICES)
    types = forms.ChoiceField(label='Type', choices=TYPE_CHOICES)
