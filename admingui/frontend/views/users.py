from django.shortcuts import get_object_or_404, render_to_response

def profile(request):
    return render_to_response('frontend/users/index.html')

def signup(request):
    return profile(request)

def login(request):
    return profile(request)

def logout(request):
    return profile(request)

def forgot(request):
    return profile(request)