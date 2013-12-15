from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *
from django.contrib import admin
from settings import STATIC_ROOT
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'eeg.views.home', name='home'),
    # url(r'^eeg/', include('eeg.foo.urls')),
    url(r'^wolves/', include('wolves.urls')), # For Alan's wolves project
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root':STATIC_ROOT}),
    
    # EEG Urls
    url(r'^chart$', 'eeg.views.chart'),
    url(r'^check_login$', 'eeg.views.check_login'),
    url(r'^post_data$', 'eeg.views.post_data'),
    url(r'^fetch$', 'eeg.views.fetch_data'),
)

