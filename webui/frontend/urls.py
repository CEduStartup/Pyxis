from django.conf.urls.defaults import *

urlpatterns = patterns('frontend.views.trackers',
    (r'^$', 'index'),
    (r'^index/$', 'index'),
    (r'^add/$', 'add'),
    (r'^edit/(\d)/?$', 'edit'),
    (r'^view/(\d)/?$', 'view'),
)

urlpatterns += patterns('',
    (r'^call$', 'frontend.views.client.tracker_data'),
)