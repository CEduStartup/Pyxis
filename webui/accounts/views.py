from django.contrib.auth.decorators import login_required
from util import render_to
from accounts.forms import UserProfileForm
from django.contrib.auth.models import User

@login_required
@render_to('accounts/profile.html')
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        if form.is_valid():
            form.save(username=request.user.username)
    else:
        form = UserProfileForm()
    return locals()
