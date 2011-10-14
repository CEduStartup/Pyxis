from django.shortcuts import get_object_or_404, render_to_response

def index(request):
    return render_to_response('frontend/index.html')