from django.conf.urls import patterns, include, url
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    'datatemplate.views',
    # url(r'^$', 'oms.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^template_mgr/$', 'template_mgr', name='template_mgr'),
    url(r'^template_dmldata/$', 'template_dmldata', name='template_dmldata'),
)