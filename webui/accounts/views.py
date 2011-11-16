from django.contrib.auth.decorators import login_required
from utils.util import render_to
from accounts.forms import UserProfileForm


@render_to('accounts/profile.html')
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
    else:
        form = UserProfileForm()
    return locals()
