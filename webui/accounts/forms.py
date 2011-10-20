from django.forms import *
from accounts.models import UserProfile
from django.contrib.auth.models import User

class UserProfileForm(Form):
    class Meta:
        model = User
    def save(self):
        pass
