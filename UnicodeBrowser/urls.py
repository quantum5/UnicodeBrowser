from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:

    url(r'^json-search/(.*)$', 'UnicodeBrowser.unicode.views.json_search'),
    url(r'fonts.css', 'UnicodeBrowser.unicode.views.fonts'),
    url(r'^$', 'UnicodeBrowser.unicode.views.search'),
    # url(r'^UnicodeBrowser/', include('UnicodeBrowser.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
