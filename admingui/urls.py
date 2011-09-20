from django.conf.urls.defaults import *

#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'frontend.views.index.index'),
)
urlpatterns += patterns('',
    (r'^users/$', 'frontend.views.users.profile'),
    *[(r'^users/%s' % action, 'frontend.views.users.%s' % action) for action in ['signup', 'login', 'logout', 'profile']] 
)
urlpatterns += patterns('',
    (r'^trackers/$', 'frontend.views.trackers.index'),
    *[(r'^trackers/%s' % action, 'frontend.views.trackers.%s' % action) for action in ['index', 'add', 'edit', 'view']] 
)
urlpatterns += patterns('',
#    (r'^admin/', include(admin.site.urls)),
)



