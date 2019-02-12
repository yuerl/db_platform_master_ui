from __future__ import unicode_literals
from django.contrib.auth.models import User
from django.db import models

read_write = (
    ('read', 'read'),
    ('write', 'write'),
    ('all','all'),
    ('idle','idle'),
)
read_write_account = (
    ('read', 'read'),
    ('write', 'write'),
    ('all','all'),
    ('admin','admin'),
)
db_type = (
    ('mysql', 'mysql'),
    ('mongodb', 'write'),
)

class Db_instance(models.Model):
    ip = models.CharField(max_length=30)
    port = models.CharField(max_length=10)
    role =  models.CharField(max_length=30,choices=read_write, )
    db_type = models.CharField(max_length=30,default='mysql')
    def __unicode__(self):
        return u'%s %s %s' % (self.ip, self.role, self.db_type)
    class Meta:
        unique_together = ("ip","port")



class Db_name (models.Model):
    dbtag = models.CharField(max_length=30,unique=True)
    dbname = models.CharField(max_length=30)
    instance = models.ManyToManyField(Db_instance)
    account = models.ManyToManyField(User)
    def __unicode__(self):
        return u'%s %s' % (self.dbtag, self.dbname)


class Db_account(models.Model):
    user = models.CharField(max_length=30)
    passwd = models.CharField(max_length=255)
    role =  models.CharField(max_length=30,choices=read_write_account,default='all')
    tags = models.CharField(max_length=30,db_index=True)
    dbname = models.ManyToManyField(Db_name)
    account = models.ManyToManyField(User)
    def __unicode__(self):
        return  u'%s %s' % ( self.tags,self.role)


class Db_group(models.Model):
    groupname = models.CharField(max_length=30,unique=True)
    dbname = models.ManyToManyField(Db_name)
    account = models.ManyToManyField(User)
    def __unicode__(self):
        return self.groupname

class Oper_log(models.Model):
    user = models.CharField(max_length=35)
    ipaddr = models.CharField(max_length=35)
    dbtag = models.CharField(max_length=35)
    dbname = models.CharField(max_length=40)
    sqltext = models.TextField()
    sqltype = models.CharField(max_length=20)
    create_time = models.DateTimeField(db_index=True)
    login_time = models.DateTimeField()
    def __unicode__(self):
        return self.dbtag
    class Meta:
        index_together = [["dbtag","sqltype", "create_time"],]

class Pro_mgr(models.Model):
    prono=models.CharField(max_length=50)
    proname = models.CharField(max_length=50)
    user= models.CharField(max_length=35)
    mgr_user =  models.CharField(max_length=35)
    status=models.CharField(max_length=30)
    create_time = models.DateTimeField(db_index=True)
    memo=models.CharField(max_length=300)
    stage=models.CharField(max_length=30)
    stage_time = models.DateTimeField(db_index=True)
    def __unicode__(self):
        return u'%s %s %s' % (self.proname, self.user, self.mgr_user)
    class Meta:
        unique_together = ("proname", "mgr_user")

class Pro_mgr_detail(models.Model):
    user = models.CharField(max_length=35)
    dbtag = models.CharField(max_length=35)
    pro_id=models.ForeignKey(to="Pro_mgr", to_field="id")
    sqltext = models.TextField()
    sql_memo=models.CharField(max_length=50,default='')
    create_time = models.DateTimeField(db_index=True)
    update_time = models.DateTimeField()
    status = models.CharField(max_length=20,db_index=True)
    sqlsha =  models.TextField()
    sche_time = models.DateTimeField(db_index=True,default='2199-01-01 00:00:00')
    operator = models.CharField(max_length=35, default='')
    add_task=models.CharField(max_length=10, default='no')
    detail_id=models.IntegerField(default=0)
    def __unicode__(self):
        return self.dbtag
# mysql_chk(hosts,type,status,msg,dtime) values("%s","mysql_uptime",1,"%s",now())
class mysql_check(models.Model):
    hosts_ip = models.CharField(max_length=35)
    chk_type = models.CharField(max_length=35)
    chk_status = models.CharField(max_length=20)
    msg=models.CharField(max_length=500)
    dtime = models.DateTimeField(db_index=True)

class mysql_check_command(models.Model):
    hosts_ip = models.CharField(max_length=35)
    command = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    count = models.IntegerField()
    dtime = models.DateTimeField(db_index=True)

class mysql_check_space(models.Model):
    hosts_ip = models.CharField(max_length=35)
    table_schema = models.CharField(max_length=50)
    table_name = models.CharField(max_length=50)
    table_rows = models.IntegerField()
    data_length = models.IntegerField()
    dtime = models.DateTimeField(db_index=True)
class mysql_hosts(models.Model):
    hosts_ip = models.CharField(max_length=35)
    host_port=models.IntegerField(default=3306)
    host_user=models.CharField(max_length=50, default='')
    host_pwd=models.CharField(max_length=100, default='')
    host_status = models.CharField(max_length=20, default='')
    dtime = models.DateTimeField(db_index=True)
#20180523 by yuerl
class mysql_dbcompare(models.Model):
    row_number=models.IntegerField()
    stype=models.CharField(max_length=30)
    host0 = models.CharField(max_length=50)
    item0 = models.CharField(max_length=100)
    host1 = models.CharField(max_length=50)
    item1 = models.CharField(max_length=100)
    result=models.TextField()
    dbtime=models.DateTimeField(db_index=True)

class mysql_initdata(models.Model):
    dbtag = models.CharField(max_length=35)
    init_table=models.CharField(max_length=100)
    init_status=models.CharField(max_length=50, default='yes')
    dtime = models.DateTimeField(db_index=True)



class Login_log(models.Model):
    user = models.CharField(max_length=35)
    ipaddr = models.CharField(max_length=35)
    action = models.CharField(max_length=20)
    create_time = models.DateTimeField(db_index=True)


class User_detail(models.Model):
    user = models.CharField(max_length=35)
    real_name = models.CharField(max_length=35)
    position = models.CharField(max_length=35)
    telephone = models.CharField(max_length=20)
    wechart = models.CharField(max_length=50)
    create_time = models.DateTimeField(db_index=True)

# class Task_scheduler(models.Model):
#     task = models.OneToOneField(Task)
#     appoint_time = models.DateTimeField(db_index=True)
#     def __unicode__(self):
#         return  self.task.id


class User_profile(models.Model):
    user = models.OneToOneField(User)
    select_limit = models.IntegerField(default=200)
    export_limit = models.IntegerField(default=200)
    task_email = models.IntegerField(db_index=True)
    def __unicode__(self):
        return  self.user.username
    class Meta:
        permissions =(('can_mysql_query','can see mysql_query view'),
                      ('can_log_query','can see log_query view'),
                      ('can_see_execview','can see mysql exec view'),
                      ('can_see_inception', 'can see inception view'),
                      ('can_see_metadata', 'can see meta_data view'),
                      ('can_see_mysqladmin', 'can see mysql_admin view'),
                      ('can_export','can export csv'),
                      ('can_insert_mysql','can insert mysql'),
                      ('can_update_mysql','can update mysql'),
                      ('can_delete_mysql','can delete mysql'),
                      ('can_create_mysql','can create mysql'),
                      ('can_drop_mysql','can drop mysql'),
                      ('can_truncate_mysql','can truncate mysql'),
                      ('can_alter_mysql','can alter mysql'),
                      ('can_query_mongo', 'can query mongo'),
                      ('can_see_taskview', 'can see task view'),
                      ('can_admin_task','can admin task'),
                      ('can_delete_task', 'can delete task'),
                      ('can_update_task', 'can update task'),
                      ('can_query_pri', 'can query pri'),
                      ('can_set_pri', 'can set pri'),
                      ('can_oper_saltapi', 'can oper saltapi'),
                      ('can_see_pro_mgr_view', 'can_see_pro_mgr_view'),
                      ('can_see_script_task_mgr', 'can_see_script_task_mgr'),
                      ('can_see_inception_dml', 'can_see_inception_dml'),
                      ('can_see_template_mgr', 'can_see_template_mgr'),
                      ('can_see_template_dmldata', 'can_see_template_dmldata'),
                      ('can_see_redisdb_query', 'can_see_redisdb_query'),
                      ('can_see_redisdb_command', 'can_see_redisdb_command'),
                      ('can_see_mongodb_query', 'can_see_mongodb_query'),
                      ('can_see_mon_mysql_mgr', 'can_see_mon_mysql_mgr'),
                      ('can_see_mysql_dashbord', 'can_see_mysql_dashbord'),
                      ('can_see_script_task_mgr_db', 'can_see_script_task_mgr_db'),
                      ('can_see_set_blist', 'can_see_set_blist'),
                      #mysql menu
                      ('can_see_mysql_menu','can_see_mysql_menu'),
                      ('can_see_mysql_menu_meta_data', 'can_see_mysql_menu_meta_data'),
                      ('can_see_mysql_menu_mysql_diff', 'can_see_mysql_menu_mysql_diff'),
                      ('can_see_mysql_menu_diff', 'can_see_mysql_menu_diff'),
                      ('can_see_mysql_menu_mysql_query', 'can_see_mysql_menu_mysql_query'),
                      ('can_see_mysql_menu_inception_dml', 'can_see_mysql_menu_inception_dml'),
                      ('can_see_mysql_menu_inception', 'can_see_mysql_menu_inception'),
                      ('can_see_mysql_menu_mysql_exec', 'can_see_mysql_menu_mysql_exec'),
                      # mysql menu
                      #oracle menu
                      ('can_see_oracle_menu', 'can_see_oracle_menu'),
                      ('can_see_oracle_menu_oracle_query', 'can_see_oracle_menu_oracle_query'),
                      ('can_see_oracle_menu_inception_dml', 'can_see_oracle_menu_inception_dml'),
                      ('can_see_oracle_menu_inception_ddldml', 'can_see_oracle_menu_inception_ddldml'),
                      ('can_see_oracle_menu_oracle_exec', 'can_see_oracle_menu_oracle_exec'),
                      # oracle menu
                      #mongodb menu
                      ('can_see_mongodb_menu', 'can_see_mongodb_menu'),
                      ('can_see_mongodb_menu_mongodb_query', 'can_see_mongodb_menu_mongodb_query'),
                      # mongodb menu
                      # redis_query menu
                      ('can_see_redis_menu', 'can_see_redis_menu'),
                      ('can_see_redis_menu_redis_query', 'can_see_redis_menu_redis_query'),
                      # redis_query menu
                      # scripts menu
                      ('can_see_scripts_menu', 'can_see_scripts_menu'),
                      ('can_see_scripts_menu_script_project_mgr','can_see_scripts_menu_script_project_mgr'),
                      ('can_see_scripts_menu_script_upload', 'can_see_scripts_menu_script_upload'),
                      ('can_see_scripts_menu_script_check_mgr', 'can_see_scripts_menu_script_check_mgr'),
                      ('can_see_scripts_menu_script_task_mgr', 'can_see_scripts_menu_script_task_mgr'),
                      ('can_see_scripts_menu_script_task_mgr_db', 'can_see_scripts_menu_script_task_mgr_db'),
                      # scripts menu
                      # task menu
                      ('can_see_task_menu', 'can_see_task_menu'),
                      ('can_see_task_menu_task_manager', 'can_see_task_menu_task_manager'),
                      # task menu
                      # dbmgr menu
                      ('can_see_dbmgr_menu', 'can_see_dbmgr_menu'),
                      ('can_see_dbmgr_menu_mon_mysql_mgr', 'can_see_dbmgr_menu_mon_mysql_mgr'),
                      ('can_see_dbmgr_menu_binlog_parse', 'can_see_dbmgr_menu_binlog_parse'),
                      ('can_see_dbmgr_menu_log_query', 'can_see_dbmgr_menu_log_query'),
                      ('can_see_dbmgr_menu_mysql_dashbord', 'can_see_dbmgr_menu_mysql_dashbord'),
                      # dbmgr menu

                      # privilges menu
                      ('can_see_privilges_menu', 'can_see_privilges_menu'),
                      ('can_see_privilges_menu_pre_query', 'can_see_privilges_menu_pre_query'),
                      ('can_see_privilges_menu_pre_set', 'can_see_privilges_menu_pre_set'),
                      ('can_see_privilges_menu_user_detail_set', 'can_see_privilges_menu_user_detail_set'),
                      ('can_see_privilges_menu_set_dbname', 'can_see_privilges_menu_set_dbname'),
                      ('can_see_privilges_menu_set_blist', 'can_see_privilges_menu_set_blist'),
                      ('can_see_privilges_menu_set_ugroup', 'can_see_privilges_menu_set_ugroup'),
                      ('can_see_privilges_menu_set_dbgroup', 'can_see_privilges_menu_set_dbgroup'),
                      # privilges menu

                      )

class Upload(models.Model):
    username = models.CharField(max_length = 40)
    filename = models.FileField(upload_to = 'upload_sql')
    def __unicode__(self):
        return self.username
# Create your models here.
class Task(models.Model):
    user = models.CharField(max_length=35)
    dbtag = models.CharField(max_length=35)
    sqltext = models.TextField()
    create_time = models.DateTimeField(db_index=True)
    update_time = models.DateTimeField()
    status = models.CharField(max_length=20,db_index=True)
    sqlsha =  models.TextField()
    sche_time = models.DateTimeField(db_index=True,default='2199-01-01 00:00:00')
    specification = models.CharField(max_length=100,default='')
    operator = models.CharField(max_length=35, default='')
    backup_status = models.SmallIntegerField(default=1)
    def __unicode__(self):
        return self.dbtag
#backup_status
# o donot  backup
# 1 need  backup
# 2



class Incep_error_log(models.Model):
    myid = models.IntegerField()
    stage = models.CharField(max_length= 20)
    errlevel = models.IntegerField()
    stagestatus = models.CharField(max_length=40)
    errormessage = models.TextField()
    sqltext = models.TextField()
    affectrow = models.IntegerField()
    sequence = models.CharField(max_length=30,db_index=True)
    backup_db = models.CharField(max_length=100)
    execute_time = models.CharField(max_length=20)
    sqlsha = models.CharField(max_length=50)
    create_time = models.DateTimeField(db_index=True)
    finish_time = models.DateTimeField()

class MySQL_monitor(models.Model):
    tag = models.CharField(max_length=20)
    monitor = models.SmallIntegerField(default=1)
    instance = models.OneToOneField(Db_instance)
    # instance = models.ForeignKey(Db_instance)
    check_longsql = models.SmallIntegerField(default=0)
    longsql_time = models.SmallIntegerField(default=1200)
    longsql_autokill = models.SmallIntegerField(default=0)
    check_active = models.SmallIntegerField(default=0)
    active_threshold = models.SmallIntegerField(default=30)
    # account = models.OneToOneField(Db_account)
    account = models.ForeignKey(Db_account)
    check_connections = models.SmallIntegerField(default=0)
    connection_threshold = models.IntegerField(default=1000)
    check_delay = models.SmallIntegerField(default=0)
    delay_threshold = models.IntegerField(default=3600)
    check_slave = models.SmallIntegerField(default=0)
    replchannel = models.CharField(max_length=30,default='0')
    alarm_times = models.SmallIntegerField(default=3)
    alarm_interval = models.SmallIntegerField(default=60)
    mail_to = models.CharField(max_length=255)
    def __unicode__(self):
        return self.tag
    class Meta:
        db_table = 'mysql_monitor'