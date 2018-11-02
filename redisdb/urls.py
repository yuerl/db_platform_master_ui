from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    'redisdb.views',
    # url(r'^$', 'oms.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^query/$', 'redis_query', name='redis_query'),
    url(r'^command/$', 'redis_command', name='redis_command'),
)
