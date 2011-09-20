import django.forms

from django.forms import ModelForm
from models import Tracker

class TrackerForm(ModelForm):
    class Meta:
        model = Tracker
        exclude = ('id', 'user', 'values_count', 'status')

