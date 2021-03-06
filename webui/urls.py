from django.conf.urls.defaults import *
from django.conf import settings

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
    (r'^trackers/', include('frontend.urls')),
    (r'^views/', include('frontend.urls_view')),
    (r'^accounts/', include('registration.urls')),
    (r'^trackerwiz/', include('trackers_wiz.urls')),
    (r'^facebook/login$', 'facebook.views.login'),
    (r'^facebook/authentication_callback$', 'facebook.views.authentication_callback'),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG is False:   #if DEBUG is True it will be served automatically
    urlpatterns += patterns('',
            url(r'^static/(?P<path>.*)$',
                'django.views.static.serve',
                {'document_root': settings.STATIC_ROOT}),)
