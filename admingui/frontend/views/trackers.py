from django.shortcuts import get_object_or_404, render_to_response

def index(request):
    return render_to_response('frontend/trackers/index.html')

def view(request):
    return index(request)

def add(request):
    return index(request)

def edit(request):
    return index(request)

def enable(request):
    return index(request)
