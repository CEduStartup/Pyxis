from django.contrib.auth.decorators import login_required
from util import render_to
from accounts.forms import UserProfileForm


@render_to('accounts/profile.html')
def profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST)
        # save
        import pdb; pdb.set_trace()
    else:
        form = UserProfileForm()
    return locals()
