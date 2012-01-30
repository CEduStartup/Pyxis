from django.conf.urls.defaults import *

from views import add, edit, get_url, try_xpath

urlpatterns = patterns('frontend.views.trackers',
    (r'^add/?', add),
    (r'^edit/(\d+)/?$', edit),
    (r'^get_url/(.+)/?$', get_url),
    (r'^try_xpath/$', try_xpath),
)
