from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.formtools.wizard import FormWizard
from django.shortcuts import get_object_or_404

from frontend.models import TrackerModel

class TrackerBaseForm(forms.ModelForm):
    class Meta:
        model = TrackerModel
	exclude = ('user', )

class TrackerGeneral(TrackerBaseForm):
    class Meta:
        model = TrackerModel
	fields = ('name', 'url')

class TrackerFormat(TrackerBaseForm):
    class Meta:
        model = TrackerModel
	fields = ('data_type',)

class TrackerPath(TrackerBaseForm):
    class Meta:
        model = TrackerModel
	fields = ('path', 'value_name')

class TrackerPollInterval(TrackerBaseForm):
    class Meta:
        model = TrackerModel
	fields = ('interval', 'interval_kind')

class TrackerPrivacy(TrackerBaseForm):
    class Meta:
        model = TrackerModel
	fields = ('privacy',)

class TrackerWizard(FormWizard):
    def get_template(self, step):
        return 'trackers_wiz/wizard.html'

    def done(self, request, form_list):
        instance = None
	if self.initial:
	    edited_id = self.initial[0].get('id')
	    if edited_id:
	        instance = get_object_or_404(TrackerModel, pk=edited_id)
        if not instance:
	    instance = TrackerModel()
	for form in form_list:
	    for field, value in form.cleaned_data.iteritems():
	        setattr(instance, field, value)
	instance.user = request.user
	instance.save()
	
        return HttpResponseRedirect('/trackers/')

