from django.conf.urls.defaults import *

from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'frontend.views.index.index'),
)
urlpatterns += patterns('',
    (r'^users/$', 'frontend.views.users.profile'),
    (r'^users/profile/$', 'accounts.views.profile'),
)
#urlpatterns += patterns('',
#    (r'^trackers/$', 'frontend.views.trackers.index'),
#    *[(r'^trackers/%s' % action, 'frontend.views.trackers.%s' % action) for action in ['index', 'add', 'edit', 'view']]
#)
#urlpatterns += patterns('',
#    (r'^tracker1s/', include('registration.urls')),
#)

urlpatterns += patterns('',
#    (r'^trackers/', include('frontend.urls')),
    (r'^accounts/', include('registration.urls')),
#    (r'^trackerwiz/', include('trackers_wiz.urls')),
    (r'^admin/', include(admin.site.urls)),
)

