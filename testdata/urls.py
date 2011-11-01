from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'testdata.views.home', name='home'),
    # url(r'^testdata/', include('testdata.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    (r'^generator/html/(?P<function>\w+)/$', 'generator.views.html'),
    (r'^generator/xml/(?P<function>\w+)/$', 'generator.views.xml'),
    (r'^generator/reset$', 'generator.views.reset')
)
