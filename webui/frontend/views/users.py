from django.shortcuts import get_object_or_404, render_to_response
from utils.util import render_to

@render_to('frontend/users/index.html')
def profile(request):
    return locals()

