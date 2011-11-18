from django.conf.urls.defaults import *

urlpatterns = patterns('frontend.views.views',
    (r'^$', 'index'),
    (r'^view/(?P<id>\d+)/?$', 'view'),
    (r'^save/?$', 'save'),
    (r'^save/(?P<id>\d+)/?$', 'save'),
    (r'^delete/(?P<id>\d+)/?$', 'delete'),
)
