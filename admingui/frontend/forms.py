from django import forms

class TrackerForm(forms.Form):
    name = forms.CharField()
    url  = forms.URLField()
    interval = forms.IntegerField()
