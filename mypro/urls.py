"""mypro URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from django.conf import settings
from myapp import views as myapp_view
urlpatterns = (
    url(r'^$', myapp_view.index, name='index'),
    url(r'^accounts/login/$',myapp_view.login,name='login'),
    url(r'^accounts/logout/$',myapp_view.logout,name='logout'),
    url(r'^admin/', admin.site.urls),
    url(r'^log_query/$', myapp_view.log_query,name='log_query'),
    url(r'^mysql_query/$', myapp_view.mysql_query,name='mysql_query'),
    url(r'^mysql_admin/$', myapp_view.mysql_admin, name='mysql_admin'),
    url(r'^binlog_parse/$', myapp_view.mysql_binlog_parse,name='binlog_parse'),
    url(r'^tb_check/$', myapp_view.tb_check, name='tb_check'),
    url(r'^dupkey_check/$', myapp_view.dupkey_check, name='dupkey_check'),
    url(r'^meta_data/$', myapp_view.meta_data,name='meta_data'),
    url(r'^mysql_exec/$', myapp_view.mysql_exec,name='mysql_exec'),
    url(r'^captcha/',include('captcha.urls')),
    url(r'^sqlcheck/$', myapp_view.inception,name='inception'),
    url(r'^task/$', myapp_view.task_manager,name='task_manager'),
    url(r'^pre_query/$', myapp_view.pre_query,name='pre_query'),
    url(r'^pass_reset/$', myapp_view.pass_reset,name='pass_reset'),
    url(r'^pre_set/$', myapp_view.pre_set,name='pre_set'),
    url(r'^user_detail_set/$', myapp_view.user_detail_set, name='user_detail_set'),
    url(r'^set_dbgroup/$', myapp_view.set_dbgroup,name='set_dbgroup'),
    url(r'^set_ugroup/$', myapp_view.set_ugroup,name='set_ugroup'),
    url(r'^fast_dbset/$', myapp_view.fast_dbset,name='fast_dbset'),
    url(r'^set_dbname/$', myapp_view.set_dbname,name='set_dbname'),
    url(r'^update_task/$', myapp_view.update_task,name='update_task'),
    url(r'^get_rollback/$', myapp_view.get_rollback,name='get_rollback'),
    url(r'^get_single_rollback/$', myapp_view.get_single_rollback,name='get_single_rollback'),
    url(r'^get_tblist/$', myapp_view.get_tblist, name='get_tblist'),
    url(r'^set_blist/$', myapp_view.set_blist, name='set_blist'),
    url(r'^mysql_diff/$', myapp_view.mysql_diff,name='mysql_diff'),
    url(r'^diff/$', myapp_view.diff,name='diff'),
    url(r'^salt/', include('salt.urls')),
    url(r'^mongodb/', include('mongodb.urls')),
    url(r'^redisdb/', include('redisdb.urls')),
    url(r'^oracle/', include('oracle.urls')),
    url(r'^datatemplate/', include('datatemplate.urls')),
    url(r'^chartapi/', include('chartapi.urls')),
    url(r'^monitor/', include('monitor.urls')),
    url(r'^myrpts/', include('myrpts.urls')),
    url(r'^passforget/', include('passforget.urls')),
    url(r'^blacklist/', include('blacklist.urls')),
    url(r'^script_project_mgr/',  myapp_view.script_project_mgr,name='script_project_mgr'),
    url(r'^script_project_mgr_download/$', myapp_view.script_project_mgr_download, name='script_project_mgr_download'),
    url(r'^script_upload/',  myapp_view.script_upload_mgr,name='script_upload'),
    url(r'^script_upload/(?P<id>\d+)/$',  myapp_view.script_upload_mgr,name='script_upload_modify'),
    # interface for demo
    url(r'^trans_script_api/',  myapp_view.trans_script_api,name='trans_script_api'),

    url(r'^script_check_mgr/',  myapp_view.script_check_mgr,name='script_check_mgr'),
    url(r'^script_test/',  myapp_view.log_query,name='script_test'),
    url(r'^inception_dml/$', myapp_view.inception_dml, name='inception_dml'),
    url(r'^script_task_mgr/',  myapp_view.script_task_mgr,name='script_task_mgr'),
    url(r'^script_task_mgr_db/', myapp_view.script_task_mgr_db, name='script_task_mgr_db'),
    # url(r'^script_task_mgr/',  myapp_view.script_task_mgr,name='script_task_mgr'),

    url(r'^mon_mysql_mgr/',  myapp_view.mon_mysql_mgr,name='mon_mysql_mgr'),
    url(r'^mysql_dashbord/',  myapp_view.mysql_dashbord,name='mysql_dashbord'),

    url(r'^site_media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),

)
handler404 = myapp_view.page_not_found
