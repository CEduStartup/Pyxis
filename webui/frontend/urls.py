from django.conf.urls.defaults import *

urlpatterns = patterns('frontend.views.trackers',
    (r'^$', 'index'),
    (r'^my$', 'private_trackers'),
    (r'^index/$', 'index'),
    #(r'^add/$', 'add'),
    #(r'^edit/(\d)/?$', 'edit'),
    (r'^view/(\d)/?$', 'view'),
)

urlpatterns += patterns('',
    (r'^call$', 'frontend.views.client.tracker_data'),
)

urlpatterns += patterns('frontend.views.value_picker',
    (r'^xml_picker/$', 'xml_picker'),
    (r'^xml_picker/load_xml/$', 'load_xml'),
)
