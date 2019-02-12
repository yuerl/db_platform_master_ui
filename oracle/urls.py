from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    'oracle.views',
    url(r'^query/$', 'oracle_query', name='oracle_query'),
    url(r'^oracle_inception_dml/$', 'oracle_inception_dml', name='oracle_inception_dml'),
    url(r'^oracle_inception_ddldml/$', 'oracle_inception_ddldml', name='oracle_inception_ddldml'),
    url(r'^oracle_exec/$', 'oracle_exec', name='oracle_exec'),
)