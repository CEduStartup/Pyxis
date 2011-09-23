from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

urlpatterns = patterns('',
    (r'^$', redirect_to, {'url': 'index'}),
    (r'^index/$', 'frontend.views.trackers.index'),
    (r'^add/$', 'frontend.views.trackers.add'),
    (r'^edit/(\d)/$', 'frontend.views.trackers.edit'),
    (r'^view/(\d)/$', 'frontend.views.trackers.view'),
)

