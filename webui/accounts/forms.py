from django.forms import *
from accounts.models import UserProfile
from django.contrib.auth.models import User

class UserProfileForm(Form):
    class Meta:
        model = User

    def save(self, username):
        user = User.objects.get(username__iexact=username)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()

    first_name  = CharField(max_length=60, required=False)
    last_name  = CharField(max_length=60, required=False)
