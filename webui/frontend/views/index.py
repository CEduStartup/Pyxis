from django.shortcuts import get_object_or_404, render_to_response
from util import render_to

@render_to('frontend/index.html')
def index(request):
    return locals()
