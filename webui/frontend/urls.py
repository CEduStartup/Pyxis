from django.conf.urls.defaults import *

urlpatterns = patterns('frontend.views.trackers',
    (r'^$', 'index'),
    (r'^my$', 'private_trackers'),
    (r'^index/$', 'index'),
    #(r'^add/$', 'add'),
    #(r'^edit/(\d)/?$', 'edit'),
    (r'^view/(\d)+/?$', 'view'),
    (r'^view/?$', 'view'),
    (r'^get_data_to_display/?$', 'get_data_to_display'),
)

urlpatterns += patterns('',
    (r'^call$', 'frontend.views.client.tracker_data'),
)
