from django.conf.urls.defaults import *

from views import *

urlpatterns = patterns('frontend.views.trackers',
    (r'^add/?', add),
    (r'^edit/(\d+)/?$', edit),
)
