#!/bin/env python
#-*-coding:utf-8-*-
import MySQLdb,sys,string,time,datetime,uuid,commands,os
from myapp.include.encrypt import prpcrypt
from django.contrib.auth.models import User,Permission,ContentType,Group
from myapp.models import Db_name,Db_account,Db_instance,Oper_log,Login_log,Db_group,Pro_mgr,Pro_mgr_detail,mysql_hosts,mysql_check,mysql_dbcompare,User_detail
from datatemplate.models import template_mgr
from myapp.form import LoginForm,Captcha
from myapp.etc import config
from mypro import settings
from django.db import connection
import mylibs


reload(sys)
sys.setdefaultencoding('utf8')
import ConfigParser
#
# def get_item(data_dict,item):
#     try:
#        item_value = data_dict[item]
#        return item_value
#     except:
#        return '-1'
#
# def get_config(group,config_name):
#     config = ConfigParser.ConfigParser()
#     config.readfp(open('./myapp/etc/config.ini','r'))
#     config_value=config.get(group,config_name).strip(' ').strip('\'').strip('\"')
#     return config_value
#
# def filters(data):
#     return data.strip(' ').strip('\n').strip('\br')
#
# host = get_config('settings','host')
# port = get_config('settings','port')
# user = get_config('settings','user')
# passwd = get_config('settings','passwd')
# dbname = get_config('settings','dbname')
# select_limit = int(get_config('settings','select_limit'))
# export_limit = int(get_config('settings','export_limit'))
# wrong_msg = get_config('settings','wrong_msg')
# public_user = get_config('settings','public_user')

# host = config.host
# port = config.port
# user = config.user
# passwd = config.passwd
# dbname = config.dbname

host = settings.DATABASES['default']['HOST']
port = settings.DATABASES['default']['PORT']
user = settings.DATABASES['default']['USER']
passwd = settings.DATABASES['default']['PASSWORD']
dbname = settings.DATABASES['default']['NAME']
select_limit = int(config.select_limit)
export_limit = int(config.export_limit)
wrong_msg = config.wrong_msg
public_user = config.public_user
sqladvisor = config.sqladvisor
advisor_switch = config.sqladvisor_switch
path_mysqldiff = config.path_to_mysqldiff
script_dir=config.script_dir
mysql_bin=config.mysql_bin

def return_dbscriptdir():
    return script_dir

def makescripts(proid):
#mgr
  try:
    stime=datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    data_pro=get_pro_data_byid(proid)
    data_detail=get_pro_mgr_by_proid(proid)
    filename=data_pro[0].prono+"_time"+stime+".sql"
    log = mylibs.MyLibs_logs(script_dir + '/', filename)
    log.log_write(str="-- time:" + stime + "\n")
    log.log_write(str="-- project_no:" + data_pro[0].prono + " project_name:"+data_pro[0].proname + "\n")
    log.log_write(str="-- manager:" +  data_pro[0].mgr_user + "\n")
    for item in data_detail:
        log.log_write(str="-- memo:"+str(item[0])+" operator:"+str(item[1])+"\n")
        log.log_write(str=str(item[2]) + "\n")
    #更新数据库脚本名称根据proid
    modify_promemo(proid,filename)
    return  filename
  except Exception, e:
    return   "failed to create file"
#mgr detail

#
# exceptlist = ["'","`","\""]
#
# def sql_init_filter(sqlfull):
#     tmp = oldp = sql = ''
#     sqllist = []
#     flag = 0
#     sqlfull = sqlfull.replace('\r','\n').strip()
#     try:
#         if sqlfull[-1]!=";":
#             sqlfull = sqlfull + ";"
#     except Exception,e:
#         pass
#     for i in sqlfull.split('\n'):
#         if len(i)>=2:
#             if i[0] == '-' and i[1] == '-' :
#                 continue
#         if len(i)>=1:
#             if i[0] == '#' :
#                 continue
#         if len(i)!=0:
#             tmp = tmp + i + '\n'
#
#     sqlfull = tmp
#     tmp = ''
#     i=0
#     while i<= (0 if len(sqlfull)==0 else len(sqlfull)-1):
#         if sqlfull[i] =='*' and oldp == '/'and flag == 0 :
#             flag = 2
#             sql = sql + sqlfull[i]
#         elif sqlfull[i] == '/' and oldp == '*' and flag == 2:
#             flag = 0
#             sql = sql + sqlfull[i]
#         elif sqlfull[i] == tmp and flag == 1:
#             flag = 0
#             sql = sql + sqlfull[i]
#             tmp=''
#         elif sqlfull[i] in exceptlist and flag == 0 and oldp != "\\":
#             tmp = sqlfull[i]
#             flag = 1
#             sql = sql + sqlfull[i]
#         elif sqlfull[i] == ';' and flag == 0:
#             sql = sql + sqlfull[i]
#             if len(sql) > 1:
#                 sqllist.append(sql)
#             sql = ''
#         # eliminate '#' among the line
#         elif sqlfull[i] == '#' and flag == 0:
#             flag =3
#         elif flag==3:
#             if sqlfull[i] == '\n':
#                 flag=0
#                 sql = sql + sqlfull[i]
#         else:
#             sql = sql + sqlfull[i]
#         oldp = sqlfull[i]
#         i=i+1
#     return sqllist
#
#
# def get_sql_detail(sqllist,flag):
#
#     query_type = ['desc','describe','show','select','explain']
#     dml_type = ['insert', 'update', 'delete', 'create', 'alter','rename', 'drop', 'truncate', 'replace']
#     if flag == 1:
#         list_type = query_type
#     elif flag ==2:
#         list_type = dml_type
#     typelist = []
#     i = 0
#     while i <= (0 if len(sqllist) == 0 else len(sqllist) - 1):
#         try:
#             type = sqllist[i].split()[0].lower()
#             if len(type)> 1:
#                 if type in list_type:
#                     #filter create or drop database,user
#                     if type == 'create' or type == 'drop' or type == 'alter':
#                         if sqllist[i].split()[1].lower() in ['database','user']:
#                             sqllist.pop(i)
#                             #i=i+1
#                             continue
#                     typelist.append(type)
#                     i = i + 1
#                 else:
#                     sqllist.pop(i)
#             else:
#                 sqllist.pop(i)
#         except:
#             i = i + 1
#
#     return sqllist


def mysql_query(sql,user=user,passwd=passwd,host=host,port=int(port),dbname=dbname,limitnum=select_limit):
    try:
        conn=MySQLdb.connect(host=host,user=user,passwd=passwd,port=int(port),connect_timeout=5,charset='utf8')
        conn.select_db(dbname)
        cursor = conn.cursor()
        count=cursor.execute(sql)
        index=cursor.description
        col=[]
        #get column name
        for i in index:
            col.append(i[0])
        #result=cursor.fetchall()
        result=cursor.fetchmany(size=int(limitnum))
        cursor.close()
        conn.close()
        return (result,col)
    except Exception,e:
        return([str(e)],''),['error']
#获取下拉菜单列表
def get_mysql_hostlist(username,tag='tag',search=''):
    dbtype='mysql'
    host_list = []
    if len(search) ==0:
        if (tag=='tag'):
            a = User.objects.get(username=username)
            #如果没有对应role='read'或者role='all'的account账号，则不显示在下拉菜单中
            # for row in a.db_name_set.all().order_by("dbtag"):
            #     if row.db_account_set.all().filter(role__in=['read','all']):
            #         if row.instance.all().filter(role__in=['read','all']).filter(db_type=dbtype):
            #             host_list.append(row.dbtag)
            # print  a.db_name_set.filter(db_account__role__in=['read','all']).filter(
            #         instance__role__in=['read','all']).filter(instance__db_type=dbtype).values(
            #         'dbtag').query;
            for row in a.db_name_set.filter(db_account__role__in=['read','all']).filter(
                    instance__role__in=['read','all']).filter(instance__db_type=dbtype).values(
                    'dbtag').distinct().order_by("dbtag"):

                host_list.append(row['dbtag'])
        elif (tag=='log'):
            # print Db_name.objects.values('dbtag').query;
            for row in Db_name.objects.values('dbtag').distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif (tag=='exec'):
            a = User.objects.get(username=username)
            #如果没有对应role='write'或者role='all'的account账号，则不显示在下拉菜单中
            # for row in a.db_name_set.all().order_by("dbtag"):
            #     if row.db_account_set.all().filter(role__in=['write','all']):
            # #排除只读实例
            #         if row.instance.all().filter(role__in=['write','all']).filter(db_type=dbtype):
            #             host_list.append(row.dbtag)

            for row in a.db_name_set.filter(db_account__role__in=['write', 'all']).filter(
                    instance__role__in=['write', 'all']).filter(instance__db_type=dbtype).values(
                    'dbtag').all().distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif (tag == 'incept'):
            a = User.objects.get(username=username)
            # for row in a.db_name_set.all().order_by("dbtag"):
            #     #find the account which is admin
            #     if row.db_account_set.all().filter(role='admin'):
            #         if row.instance.all().filter(role__in=['write','all']).filter(db_type=dbtype):
            #         #if row.instance.all().exclude(role='read'):
            #             host_list.append(row.dbtag)
            for row in a.db_name_set.filter(db_account__role='admin').filter(
                    instance__role__in=['write', 'all']).filter(instance__db_type=dbtype).values(
                    'dbtag').all().distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif (tag == 'meta'):
            # print Db_name.objects.filter(db_account__role='admin').filter(
            #     instance__role__in=['write', 'all', 'read']).filter(instance__db_type=dbtype).values(
            #     'dbtag').all().query
            for row in Db_name.objects.filter(db_account__role='admin').filter(
                    instance__role__in=['write', 'all','read']).filter(instance__db_type=dbtype).values(
                    'dbtag').all().distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])


    elif len(search) > 0:
        if (tag=='tag'):
            a = User.objects.get(username=username)
            #如果没有对应role='read'或者role='all'的account账号，则不显示在下拉菜单中
            # for row in a.db_name_set.filter(dbname__contains=search).order_by("dbtag"):
            #     if row.db_account_set.all().filter(role__in=['read','all']):
            #         if row.instance.all().filter(role__in=['read','all']).filter(db_type=dbtype):
            #             host_list.append(row.dbtag)
            for row in a.db_name_set.filter(dbname__contains=search).filter(db_account__role__in=['read', 'all']).filter(
                    instance__role__in=['read', 'all']).filter(instance__db_type=dbtype).values(
                    'dbtag').distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif (tag=='log'):
            for row in Db_name.objects.values('dbtag').distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif (tag=='exec'):
            a = User.objects.get(username=username)
            #如果没有对应role='write'或者role='all'的account账号，则不显示在下拉菜单中
            # for row in a.db_name_set.filter(dbname__contains=search).order_by("dbtag"):
            #     if row.db_account_set.all().filter(role__in=['write','all']):
            # #排除只读实例
            #         if row.instance.all().filter(role__in=['write','all']).filter(db_type=dbtype):
            #             host_list.append(row.dbtag)
            for row in a.db_name_set.filter(dbname__contains=search).filter(db_account__role__in=['write', 'all']).filter(
                    instance__role__in=['write', 'all']).filter(instance__db_type=dbtype).values(
                    'dbtag').all().distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif (tag == 'incept'):
            a = User.objects.get(username=username)
            # for row in a.db_name_set.filter(dbname__contains=search).order_by("dbtag"):
            #     #find the account which is admin
            #     if row.db_account_set.all().filter(role='admin'):
            #         if row.instance.all().filter(role__in=['write','all']).filter(db_type=dbtype):
            #         #if row.instance.all().exclude(role='read'):
            #             host_list.append(row.dbtag)
            for row in a.db_name_set.filter(dbname__contains=search).filter(db_account__role='admin').filter(
                    instance__role__in=['write', 'all']).filter(instance__db_type=dbtype).values(
                    'dbtag').all().distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif (tag == 'meta'):
            # for row in Db_name.filter(dbname__contains=search).order_by("dbtag"):
            #     #find the account which is admin
            #     if row.db_account_set.all().filter(role='admin'):
            #         if row.instance.filter(role__in=['write','all','read']).filter(db_type=dbtype):
            #             host_list.append(row.dbtag)
            '''print Db_name.objects.filter(dbname__contains=search).filter(db_account__role='admin').filter(
                    instance__role__in=['write', 'all','read']).filter(instance__db_type=dbtype).values(
                    'dbtag').all().query;'''
            for row in Db_name.objects.filter(dbname__contains=search).filter(db_account__role='admin').filter(
                    instance__role__in=['write', 'all','read']).filter(instance__db_type=dbtype).values(
                    'dbtag').all().distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])

    return host_list



#获取下拉菜单列表
def get_mysql_oracle_hostlist(username,tag='tag',search=''):
    host_list = []
    if len(search) ==0:
        if (tag=='tag'):
            a = User.objects.get(username=username)
            for row in a.db_name_set.filter(db_account__role__in=['read','all']).filter(
                    instance__role__in=['read','all']).filter(instance__db_type__in=['mysql','Oracle']).values(
                    'dbtag').distinct().order_by("dbtag"):

                host_list.append(row['dbtag'])
        elif (tag=='log'):
            # print Db_name.objects.values('dbtag').query;
            for row in Db_name.objects.values('dbtag').distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif (tag=='exec'):
            a = User.objects.get(username=username)
            #如果没有对应role='write'或者role='all'的account账号，则不显示在下拉菜单中
            # for row in a.db_name_set.all().order_by("dbtag"):
            #     if row.db_account_set.all().filter(role__in=['write','all']):
            # #排除只读实例
            #         if row.instance.all().filter(role__in=['write','all']).filter(db_type=dbtype):
            #             host_list.append(row.dbtag)

            for row in a.db_name_set.filter(db_account__role__in=['write', 'all']).filter(
                    instance__role__in=['write', 'all']).filter(instance__db_type__in=['mysql','Oracle']).values(
                    'dbtag').all().distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif (tag == 'incept'):
            a = User.objects.get(username=username)
            # for row in a.db_name_set.all().order_by("dbtag"):
            #     #find the account which is admin
            #     if row.db_account_set.all().filter(role='admin'):
            #         if row.instance.all().filter(role__in=['write','all']).filter(db_type=dbtype):
            #         #if row.instance.all().exclude(role='read'):
            #             host_list.append(row.dbtag)
            for row in a.db_name_set.filter(db_account__role='admin').filter(
                    instance__role__in=['write', 'all']).filter(instance__db_type__in=['mysql','Oracle']).values(
                    'dbtag').all().distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif (tag == 'meta'):
            # print Db_name.objects.filter(db_account__role='admin').filter(
            #     instance__role__in=['write', 'all', 'read']).filter(instance__db_type=dbtype).values(
            #     'dbtag').all().query
            for row in Db_name.objects.filter(db_account__role='admin').filter(
                    instance__role__in=['write', 'all','read']).filter(instance__db_type__in=['mysql','Oracle']).values(
                    'dbtag').all().distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])


    elif len(search) > 0:
        if (tag=='tag'):
            a = User.objects.get(username=username)
            #如果没有对应role='read'或者role='all'的account账号，则不显示在下拉菜单中
            # for row in a.db_name_set.filter(dbname__contains=search).order_by("dbtag"):
            #     if row.db_account_set.all().filter(role__in=['read','all']):
            #         if row.instance.all().filter(role__in=['read','all']).filter(db_type=dbtype):
            #             host_list.append(row.dbtag)
            for row in a.db_name_set.filter(dbname__contains=search).filter(db_account__role__in=['read', 'all']).filter(
                    instance__role__in=['read', 'all']).filter(instance__db_type__in=['mysql','Oracle']).values(
                    'dbtag').distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif (tag=='log'):
            for row in Db_name.objects.values('dbtag').distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif (tag=='exec'):
            a = User.objects.get(username=username)
            #如果没有对应role='write'或者role='all'的account账号，则不显示在下拉菜单中
            # for row in a.db_name_set.filter(dbname__contains=search).order_by("dbtag"):
            #     if row.db_account_set.all().filter(role__in=['write','all']):
            # #排除只读实例
            #         if row.instance.all().filter(role__in=['write','all']).filter(db_type=dbtype):
            #             host_list.append(row.dbtag)
            for row in a.db_name_set.filter(dbname__contains=search).filter(db_account__role__in=['write', 'all']).filter(
                    instance__role__in=['write', 'all']).filter(instance__db_type__in=['mysql','Oracle']).values(
                    'dbtag').all().distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif (tag == 'incept'):
            a = User.objects.get(username=username)
            # for row in a.db_name_set.filter(dbname__contains=search).order_by("dbtag"):
            #     #find the account which is admin
            #     if row.db_account_set.all().filter(role='admin'):
            #         if row.instance.all().filter(role__in=['write','all']).filter(db_type=dbtype):
            #         #if row.instance.all().exclude(role='read'):
            #             host_list.append(row.dbtag)
            for row in a.db_name_set.filter(dbname__contains=search).filter(db_account__role='admin').filter(
                    instance__role__in=['write', 'all']).filter(instance__db_type__in=['mysql','Oracle']).values(
                    'dbtag').all().distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif (tag == 'meta'):
            # for row in Db_name.filter(dbname__contains=search).order_by("dbtag"):
            #     #find the account which is admin
            #     if row.db_account_set.all().filter(role='admin'):
            #         if row.instance.filter(role__in=['write','all','read']).filter(db_type=dbtype):
            #             host_list.append(row.dbtag)
            '''print Db_name.objects.filter(dbname__contains=search).filter(db_account__role='admin').filter(
                    instance__role__in=['write', 'all','read']).filter(instance__db_type=dbtype).values(
                    'dbtag').all().query;'''
            for row in Db_name.objects.filter(dbname__contains=search).filter(db_account__role='admin').filter(
                    instance__role__in=['write', 'all','read']).filter(instance__db_type__in=['mysql','Oracle']).values(
                    'dbtag').all().distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])

    return host_list



def get_op_type(methods='get'):
    #all表示所有种类
    op_list=['all','incept','truncate','drop','create','delete','update','replace','insert','select','explain','alter','rename','show']
    if (methods=='get'):
        return op_list


def get_connection_info(hosttag,request):
    # 确认dbname
    a = Db_name.objects.filter(dbtag=hosttag)[0]
    # a = Db_name.objects.get(dbtag=hosttag)
    tar_dbname = a.dbname
    # 如果instance中有备库role='read'，则选择从备库读取
    try:
        if a.instance.all().filter(role='read')[0]:
            tar_host = a.instance.all().filter(role='read')[0].ip
            tar_port = a.instance.all().filter(role='read')[0].port
    # 如果没有设置或没有role=read，则选择第一个读到的all实例读取
    except Exception, e:
        tar_host = a.instance.filter(role='all')[0].ip
        tar_port = a.instance.filter(role='all')[0].port
        # tar_host = a.instance.all()[0].ip
        # tar_port = a.instance.all()[0].port
    pc = prpcrypt()
    for i in a.db_account_set.all():
        if i.role != 'write' and i.role != 'admin':
            # find the specified account for the user
            if i.account.all().filter(username=request.user.username):
                tar_username = i.user
                tar_passwd = pc.decrypt(i.passwd)
                break
    # not find specified account for the user ,specified the public account to the user

    if not vars().has_key('tar_username'):
        for i in a.db_account_set.all():
            if i.role != 'write' and i.role != 'admin':
                # find the specified account for the user
                if i.account.all().filter(username=public_user):
                    tar_username = i.user
                    tar_passwd = pc.decrypt(i.passwd)
                    break
    return tar_port,tar_passwd,tar_username,tar_host,tar_dbname


def get_advice(hosttag, sql, request):
    if advisor_switch!=0:
        tar_port, tar_passwd, tar_username, tar_host,tar_dbname = get_connection_info(hosttag,request)
        # print tar_port+tar_passwd+tar_username+tar_host
        sql=sql.replace('"','\\"').replace('`', '\`')[:-1]
        cmd = sqladvisor+ ' -u %s -p %s -P %d -h %s -d %s -v 1 -q "%s"' %(tar_username,tar_passwd,int(tar_port),tar_host,tar_dbname,sql)
        # print cmd
        status,result_tmp = commands.getstatusoutput(cmd)
        # print result_tmp
        result_list = result_tmp.split('\n')
        results=''
        for i in result_list:
            try:
                unicode(i, 'utf-8')
                results=results+'\n'+i
            except Exception,e:
                pass
        #print results
    else:
        results = 'sqladvisor not configured yet.'
    return results


def get_mysql_data(hosttag,sql,useraccount,request,limitnum):
    #确认dbname
    a = Db_name.objects.filter(dbtag=hosttag)[0]
    #a = Db_name.objects.get(dbtag=hosttag)
    tar_dbname = a.dbname
    #如果instance中有备库role='read'，则选择从备库读取
    try:
        if a.instance.all().filter(role='read')[0]:
            tar_host = a.instance.all().filter(role='read')[0].ip
            tar_port = a.instance.all().filter(role='read')[0].port
    #如果没有设置或没有role=read，则选择第一个读到的all实例读取
    except Exception,e:
        tar_host = a.instance.filter(role='all')[0].ip
        tar_port = a.instance.filter(role='all')[0].port
        # tar_host = a.instance.all()[0].ip
        # tar_port = a.instance.all()[0].port
    pc = prpcrypt()
    for i in a.db_account_set.all():
        if i.role!='write' and i.role!='admin':
            # find the specified account for the user
            if i.account.all().filter(username=useraccount):
                tar_username = i.user
                tar_passwd = pc.decrypt(i.passwd)
                break
    #not find specified account for the user ,specified the public account to the user
    if not vars().has_key('tar_username'):
        for i in a.db_account_set.all():
            if i.role != 'write' and i.role != 'admin':
                # find the specified account for the user
                if i.account.all().filter(username=public_user):
                    tar_username = i.user
                    tar_passwd = pc.decrypt(i.passwd)
                    break
    #print tar_port+tar_passwd+tar_username+tar_host
    try:
        if (cmp(sql,wrong_msg)):
            log_mysql_op(useraccount,sql,tar_dbname,hosttag,request)
        results,col = mysql_query(sql,tar_username,tar_passwd,tar_host,tar_port,tar_dbname,limitnum)
    except Exception, e:
        #防止日志库记录失败，返回一个wrong_message
        results,col = ([str(e)],''),['error']
        #results,col = mysql_query(wrong_msg,user,passwd,host,int(port),dbname)
    return results,col,tar_dbname


#检查输入语句,并返回行限制数
def check_mysql_query(sqltext,user,type='select'):
    #根据user确定能够select或者export 的行数
    if (type=='export'):
        try :
            num = User.objects.get(username=user).user_profile.export_limit
        except Exception, e:
            num = export_limit
    elif (type=='select'):
        try :
            num = User.objects.get(username=user).user_profile.select_limit
        except Exception, e:
            num = select_limit
    num=str(num)
    limit = ' limit ' + num

    sqltext = sqltext.strip()
    sqltype = sqltext.split()[0].lower()
    list_type = ['select','show','desc','explain','describe']
    #flag 1位有效 0为list_type中的无效值
    flag=0
    while True:
        sqltext = sqltext.strip()
        lastletter = sqltext[len(sqltext)-1]
        if (not cmp(lastletter,';')):
            sqltext = sqltext[:-1]
        else:
            break
    #判断语句中是否已经存在limit，has_limit 为0时说明原来语句中是有limit的
    try:
        has_limit = cmp(sqltext.split()[-2].lower(),'limit')
    except Exception,e:
        #prevent some input like '1' or 'ss' ...
        return wrong_msg, num

    for i in list_type:
        if (not cmp(i,sqltype)):
            flag=1
            break
    if (flag==1):
        if (sqltype =='select' and has_limit!=0):
            return sqltext+limit,num
        elif (sqltype =='select' and has_limit==0):
            if (int(sqltext.split()[-1])<= int(num) ):
                return sqltext,num
            else:
                tempsql=''
                numlimit=sqltext.split()[-1]
                for i in sqltext.split()[0:-1]:
                    tempsql=tempsql+i+' '
                return tempsql+num,num
        else:
            return sqltext,num
    else:
        return wrong_msg,num

#记录用户所有操作
def log_mysql_op(user,sqltext,mydbname,dbtag,request):
    user = User.objects.get(username=user)
    #lastlogin = user.last_login+datetime.timedelta(hours=8)
    #create_time = datetime.datetime.now()+datetime.timedelta(hours=8)
    lastlogin = user.last_login
    create_time = datetime.datetime.now()
    username = user.username
    sqltype=sqltext.split()[0].lower()
    if sqltype in ['desc','describe']:
        sqltype='show'
    #获取ip地址
    ipaddr = get_client_ip(request)
    log = Oper_log (user=username,sqltext=sqltext,sqltype=sqltype,login_time=lastlogin,create_time=create_time,dbname=mydbname,dbtag=dbtag,ipaddr=ipaddr)
    log.save()
    return 1

def log_mongo_op(sqltext,dbtag,tbname,request):
    user = User.objects.get(username=request.user.username)
    lastlogin = user.last_login
    create_time = datetime.datetime.now()
    username = user.username
    sqltype='select'
    ipaddr = get_client_ip(request)
    log = Oper_log (user=username,sqltext=sqltext,sqltype=sqltype,login_time=lastlogin,create_time=create_time,dbname=tbname,dbtag=dbtag,ipaddr=ipaddr)
    log.save()
    return 1


def log_redis_op(sqltext,dbtag,request):
    user = User.objects.get(username=request.user.username)
    lastlogin = user.last_login
    create_time = datetime.datetime.now()
    username = user.username
    sqltype='select'
    ipaddr = get_client_ip(request)
    log = Oper_log (user=username,sqltext=sqltext,sqltype=sqltype,login_time=lastlogin,create_time=create_time,dbname=dbtag,dbtag=dbtag,ipaddr=ipaddr)
    log.save()
    return 1

def log_mongo_log(sqltext,dbtag,request):
    user = User.objects.get(username=request.user.username)
    lastlogin = user.last_login
    create_time = datetime.datetime.now()
    username = user.username
    sqltype='select'
    ipaddr = get_client_ip(request)
    log = Oper_log (user=username,sqltext=sqltext,sqltype=sqltype,login_time=lastlogin,create_time=create_time,dbname="null",dbtag=dbtag,ipaddr=ipaddr)
    log.save()
    return 1


def log_userlogin(request):
    username = request.user.username
    user = User.objects.get(username=username)
    ipaddr = get_client_ip(request)
    action = 'login'
    create_time = datetime.datetime.now()
    log = Login_log(user=username,ipaddr=ipaddr,action=action,create_time=create_time)
    log.save()

def log_loginfailed(request,username):

    ipaddr = get_client_ip(request)
    action = 'login_failed'
    create_time = datetime.datetime.now()
    log = Login_log(user=username, ipaddr=ipaddr, action=action,create_time=create_time)
    log.save()

def log_loginout(request,username):
    ipaddr = get_client_ip(request)
    action = 'login_out'
    create_time = datetime.datetime.now()
    log = Login_log(user=username, ipaddr=ipaddr, action=action,create_time=create_time)
    log.save()


def get_log_data(dbtag,optype,begin,end):
    if (optype=='all'):
        #如果结束时间小于开始时间，则以结束时间为准
        if (end > begin):
            log = Oper_log.objects.filter(dbtag=dbtag).filter(create_time__lte=end).filter(create_time__gte=begin).order_by("-create_time")[0:100]
        else:
            log = Oper_log.objects.filter(dbtag=dbtag).filter(create_time__lte=end).order_by("-create_time")[0:100]
    else:
        if (end > begin):
            log = Oper_log.objects.filter(dbtag=dbtag).filter(sqltype=optype).filter(create_time__lte=end).filter(create_time__gte=begin).order_by("-create_time")[0:100]
        else:
            log = Oper_log.objects.filter(dbtag=dbtag).filter(sqltype=optype).filter(create_time__lte=end).order_by("-create_time")[0:100]
    return log

def get_pro_data(proname):
    if len(proname)>0:
        datalist = Pro_mgr.objects.filter(proname__contains=proname).order_by("-create_time")[0:100]
    else:
        datalist = Pro_mgr.objects.all().order_by("-create_time")[0:100]
    return datalist


def get_template_dmldata(tmpname):
    if len(tmpname)>0:
        datalist = template_mgr.objects.filter(templtename__contains=tmpname).order_by("-create_time")[0:100]
    else:
        datalist = template_mgr.objects.all().order_by("-create_time")[0:100]
    return datalist

def get_template_data_by_tmp_no(tmp_no):
    if len(tmp_no)>0:
        datalist = template_mgr.objects.filter(templteno__contains=tmp_no).order_by("-create_time")[0:100]
    else:
        datalist = template_mgr.objects.all().order_by("-create_time")[0:100]
    return datalist

def get_template_demo(tmpname):
    temp_list = []
    if len(tmpname)>0:
        datalist = template_mgr.objects.values('id', 'templteno', 'templtename').filter(templtename__contains=tmpname).filter(templtestatus__in=['created','modified']).order_by("-create_time")
    else:
        datalist = template_mgr.objects.values('id', 'templteno', 'templtename').filter(templtestatus__in=['created','modified']).order_by("-create_time")
    for row in datalist:
        temp_list.append(row['templteno']+','+row['templtename'])
    if len(datalist)==0:
        temp_list.append('---Please Refresh---')
    return temp_list

def get_pro_list():
     datalist = Pro_mgr.objects.values('id','prono','proname').filter(status__in=['created','modified','finished'] ).order_by("-create_time")[0:100]
     return datalist


def get_pro_list_unfinish():
    datalist = Pro_mgr.objects.values('id', 'prono', 'proname').filter(
        status__in=['created', 'modified']).order_by("-create_time")[0:100]
    return datalist

def get_pro_list_cm():
    datalist = Pro_mgr.objects.values('id', 'prono', 'proname').filter(
        status__in=['created', 'modified','finished']).order_by("-create_time")[0:100]
    return datalist



def get_pro_list_cm():
    datalist = Pro_mgr.objects.values('id', 'prono', 'proname').filter(
        status__in=['created', 'modified','finished']).order_by("-create_time")[0:100]
    return datalist

#返回数据库的类型是mysql\oracle\redis\mongodb
def get_dbtype_bydbtag(dbtag):
    with connection.cursor() as cursor:
        sql_str="SELECT c.db_type,a.dbname FROM myapp_db_name a JOIN myapp_db_name_instance b ON a.id=b.db_name_id  JOIN myapp_db_instance c ON b.db_instance_id=c.id WHERE a.dbtag=%s  LIMIT 1"
        cursor.execute(sql_str,[dbtag])
        row = cursor.fetchall()
    cursor.close()
    return row

def create_pro(prono,proname,user_mgr,status,user,createtime,stage_mgr,stage_time):
    if len(prono)>0 and len(proname)>0:
        #user = User.objects.create_user(username=username,password=passwd,email=mail)
        dic = {'prono':prono ,'proname':proname ,'user':user,'mgr_user':user_mgr,'status':status,'create_time':createtime,'stage':stage_mgr,'stage_time':stage_time}
        pro_mgr=Pro_mgr.objects.create(**dic)
    return pro_mgr

def create_template(templteno,templtename,templtestatus,templtememo,create_user,createtime, a):
    if len(templteno)>0 and len(templtename)>0:
        #user = User.objects.create_user(username=username,password=passwd,email=mail)
        dic = {'templteno':templteno ,'templtename':templtename ,'templtestatus':templtestatus ,'templtememo':templtememo ,'create_user':create_user ,'create_time':createtime ,'sqltext':a,'update_time': createtime}
        pro_mgr=template_mgr.objects.create(**dic)
    return pro_mgr

def modify_pro(id,prono,proname,user_mgr,status,stage_mgr,stage_time):
    if len(id)>0 and len(prono)>0:
        obj = Pro_mgr.objects.get(id=id)
        obj.prono = prono
        obj.proname = proname
        obj.mgr_user = user_mgr
        obj.status = status
        obj.stage=stage_mgr
        obj.stage_time=stage_time
        obj.save()
def modify_promemo(id,memo):
    if len(id)>0:
        obj = Pro_mgr.objects.get(id=id)
        obj.memo=memo
        obj.save()

def modify_template(id,templteno,templtename,templtememo,create_user,sqltext,templtestatus):
    if len(id)>0 and len(templteno)>0:
        obj = template_mgr.objects.get(id=id)
        obj.templteno = templteno
        obj.templtename=templtename
        obj.templtememo=templtememo
        obj.sqltext=sqltext
        obj.templtestatus=templtestatus
        obj.update_time=datetime.datetime.now()
        obj.save()

def delete_pro(id):
    if len(id)>0:
        obj = Pro_mgr.objects.filter(id=id).delete()
        return  0;
    else:
        return -1;
def delete_template(id):
    if len(id)>0:
        obj = template_mgr.objects.filter(id=id).delete()
        return  0;
    else:
        return -1;
def get_pro_mgr_list(dbtag,id):
    if len(id)>0:
        # create_time, dbtag, id, operator, pro_id, pro_id_id, sche_time, sql_memo, sqlsha, sqltext, status, update_time, user
        #print Pro_mgr_detail.objects.filter(pro_id__id=id).filter(pro_id=id).filter(dbtag=dbtag).query
        # data2 = get_pro_data(id)
        datalist = Pro_mgr_detail.objects.filter(pro_id__id=id).filter(pro_id=id).filter(dbtag=dbtag).order_by("create_time")
        # while i < len(datalist)
        #     datalist[i]
        # print Pro_mgr_detail.objects.filter(pro_id__id=id).filter(pro_id=id).filter(dbtag=dbtag).query
        return  datalist;
    else:
        return "";
def get_pro_data_byid(id):
    datalist = Pro_mgr.objects.filter(id=id)
    return datalist
def get_pro_mgr_by_detailid(id):
    if len(id)>0:
        # with connection.cursor() as cursor:
        #     sql_str = "SELECT a.`sql_memo`,a.`operator`,a.`sqltext` FROM  myapp_pro_mgr_detail a  where a.pro_id_id=%s and  a.`detail_id` not in (select id from myapp_pro_mgr_detail where pro_id_id=%s)"
        #     cursor.execute(sql_str, [id,id])
        #     row = cursor.fetchall()
        # cursor.close()
        # create_time, dbtag, id, operator, pro_id, pro_id_id, sche_time, sql_memo, sqlsha, sqltext, status, update_time, user
        datalist = Pro_mgr_detail.objects.filter(id=id)
        return  datalist;
    else:
        return "";
def get_pro_mgr_by_proid(pro_id):
    if len(pro_id)>0:
        # create_time, dbtag, id, operator, pro_id, pro_id_id, sche_time, sql_memo, sqlsha, sqltext, status, update_time, user
    #     datalist = Pro_mgr_detail.objects.filter(pro_id=pro_id).filter(pro_id__stage='pro')
    #     return  datalist;
    # else:
    #     return "";
        with connection.cursor() as cursor:
            sql_str = "SELECT a.`sql_memo`,a.`operator`,a.`sqltext` FROM  myapp_pro_mgr_detail a  where a.pro_id_id=%s and  a.`detail_id` not in (select id from myapp_pro_mgr_detail where pro_id_id=%s)"
            cursor.execute(sql_str, [pro_id, pro_id])
            row = cursor.fetchall()
            cursor.close()
        return row


def delete_pro_mgr_by_detailid(id):
    if len(id)>0:
        # create_time, dbtag, id, operator, pro_id, pro_id_id, sche_time, sql_memo, sqlsha, sqltext, status, update_time, user
        datalist = Pro_mgr_detail.objects.filter(id=id).delete()
        return  datalist;
    else:
        return "";

#insert into trans
def pro_mgr_detail_trans(dbtag_source,dbtag_target,pro_id):
    with connection.cursor() as cursor:
        sql_str="INSERT INTO `myapp_pro_mgr_detail` ( `user`, `dbtag`, `pro_id_id`, `sqltext`, `create_time`, `update_time`, `status`, `sqlsha`, `sche_time`, `operator`, `sql_memo`, `add_task`, `detail_id`)"
        sql_str=sql_str+ "SELECT  'admin', %s, `pro_id_id`, `sqltext`,create_time,NOW(),'created',`sqlsha`,`sche_time`,`operator`, `sql_memo`,'no',`id`"
        sql_str = sql_str + " FROM myapp_pro_mgr_detail WHERE `dbtag`=%s AND `pro_id_id`=%s"
        sql_str = sql_str +" AND id NOT IN (SELECT  detail_id FROM myapp_pro_mgr_detail WHERE `dbtag`=%s AND `pro_id_id`=%s)"
        row=cursor.execute(sql_str, [dbtag_target,dbtag_source,pro_id ,dbtag_target,pro_id])
    return row

#insert into trans api
def pro_mgr_detail_trans_api(dbtag_source,dbtag_target):
    with connection.cursor() as cursor:
        sql_str="INSERT INTO `myapp_pro_mgr_detail` ( `user`, `dbtag`, `pro_id_id`, `sqltext`, `create_time`, `update_time`, `status`, `sqlsha`, `sche_time`, `operator`, `sql_memo`, `add_task`, `detail_id`)"
        sql_str=sql_str+ "SELECT  'admin', %s, `pro_id_id`, `sqltext`,create_time,NOW(),'finished',`sqlsha`,`sche_time`,`operator`, CONCAT(`sql_memo`,'_!@#trans_api'),'yes',`id`"
        sql_str = sql_str + " FROM myapp_pro_mgr_detail WHERE `dbtag`=%s "
        sql_str = sql_str +" AND id NOT IN (SELECT  detail_id FROM myapp_pro_mgr_detail WHERE `dbtag`=%s)"
        row=cursor.execute(sql_str, [dbtag_target,dbtag_source ,dbtag_target])
    return row
#insert into trans api
def pro_mgr_detail_trans_task_api(dbtag_source,dbtag_target):
    with connection.cursor() as cursor:
        sql_str="INSERT INTO  myapp_task ( `user`, `dbtag`, `sqltext`, `create_time`, `update_time`, `status`, `sqlsha`, `sche_time`, `specification`, `operator`, `backup_status`)"
        sql_str=sql_str+"SELECT  'admin',`dbtag`,`sqltext`,create_time,NOW(),'running',`sqlsha`,`sche_time`,CONCAT('api','source',%s,'target',%s,'key:',id),`operator`, 1"
        sql_str = sql_str + "  FROM myapp_pro_mgr_detail WHERE sql_memo LIKE '%_!@#trans_api' "
        row=cursor.execute(sql_str, [dbtag_source ,dbtag_target])
    return row


def pro_mgr_detail_get_db_diff(dbtag_source,dbtag_target):
    with connection.cursor() as cursor:
        sql_str="SELECT  a.`id`,b.`prono`,b.`proname`,a.`operator`,a.`dbtag`,a.`sql_memo`,a.`add_task`,a.`sqltext`,a.`status`,a.`create_time`,a.`update_time`"
        sql_str = sql_str + "  FROM myapp_pro_mgr_detail a JOIN myapp_pro_mgr b ON a.`pro_id_id`=b.`id` WHERE a.`dbtag`=%s "
        sql_str = sql_str +"  AND a.id NOT IN (SELECT  detail_id FROM myapp_pro_mgr_detail WHERE `dbtag`=%s) ORDER BY b.`stage_time`,a.`create_time` "
        cursor.execute(sql_str, [dbtag_source ,dbtag_target])
        row=cursor.fetchall()
        cursor.close()
    return row


#insert into trans api
def pro_mgr_detail_insert_db_diff(dbtag_source,dbtag_target,user):
    with connection.cursor() as cursor:
        sql_str="INSERT INTO `myapp_pro_mgr_detail` ( `user`, `dbtag`, `pro_id_id`, `sqltext`, `create_time`, `update_time`, `status`, `sqlsha`, `sche_time`, `operator`, `sql_memo`, `add_task`, `detail_id`)"
        sql_str=sql_str   + "SELECT  %s, %s, a.`pro_id_id`, a.`sqltext`,a.create_time,NOW(),'created',a.`sqlsha`,a.`sche_time`,%s, CONCAT(a.`sql_memo`,'_!@#trans_api'),'yes',a.`id`"
        sql_str = sql_str + " FROM myapp_pro_mgr_detail a join myapp_pro_mgr b ON a.`pro_id_id`=b.`id`  WHERE a.`dbtag`=%s "
        sql_str = sql_str +" AND a.id NOT IN (SELECT  detail_id FROM myapp_pro_mgr_detail WHERE `dbtag`=%s) ORDER BY b.`stage_time`,a.`create_time` "
        row=cursor.execute(sql_str, [user,dbtag_target,user,dbtag_source ,dbtag_target])
    return row

def pro_mgr_detail_task(user,dbtag_target):
    with connection.cursor() as cursor:
        sql_str="INSERT INTO  myapp_task ( `user`, `dbtag`, `sqltext`, `create_time`, `update_time`, `status`, `sqlsha`, `sche_time`, `specification`, `operator`, `backup_status`)"
        sql_str=sql_str+" SELECT  %s,`dbtag`,GROUP_CONCAT(sqltext SEPARATOR '\n') sqltext ,NOW(),NOW() ,'running', sqlsha,sche_time,GROUP_CONCAT(id SEPARATOR ';') specification, %s,1 "
        sql_str = sql_str + "    FROM myapp_pro_mgr_detail WHERE sql_memo LIKE '%%_!@#trans_api' AND `status`='created' and dbtag=%s "
        sql_str = sql_str +" GROUP BY   %s,`dbtag`,NOW(),NOW() ,'running',sqlsha,sche_time, %s,1 "
        row=cursor.execute(sql_str,[user,user,dbtag_target,user,user])
    return row

def pro_mgr_detail_update_db_diff(dbtag_target):
    with connection.cursor() as cursor:
        sql_str="UPDATE myapp_pro_mgr_detail SET `status`='finished' WHERE sql_memo LIKE '%%!@#trans_api' and  `status`='created' and dbtag=%s "
        row=cursor.execute(sql_str,[dbtag_target])
    return row

def check_explain (sqltext):
    sqltext = sqltext.strip()
    sqltype = sqltext.split()[0].lower()
    if (sqltype =='select'):
        sqltext = 'explain extended '+sqltext
        return sqltext
    else:
        return wrong_msg
#
# def my_key(group, request):
#     try:
#         real_ip = request.META['HTTP_X_FORWARDED_FOR']
#         regip = real_ip.split(",")[0]
#     except:
#         try:
#             regip = request.META['REMOTE_ADDR']
#         except:
#             regip = ""
#     form = LoginForm(request.POST)
#     myform = Captcha(request.POST)
#     #验证码正确情况下，错误密码登录次数
#     if form.is_valid() and myform.is_valid():
#         username = form.cleaned_data['username']
#         # password = form.cleaned_data['password']
#
#         return regip+username
#     #验证码错误不计算
#     else:
#         return regip+str(uuid.uuid1())


def get_client_ip(request):
    try:
        real_ip = request.META['HTTP_X_FORWARDED_FOR']
        regip = real_ip.split(",")[0]
    except:
        try:
            regip = request.META['REMOTE_ADDR']
        except:
            regip = ""
    return regip

def check_mysql_exec(sqltext,request,type='dml'):
    # request.user.has_perm('myapp.')
    sqltext = sqltext.strip()
    sqltype = sqltext.split()[0].lower()
    list_type = ['insert','update','delete','create','alter','rename','drop','truncate','replace']
    if (sqltype=='insert'):
        if request.user.has_perm('myapp.can_insert_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"insert\"'"
    elif(sqltype=='update' or sqltype == 'replace'):
        if request.user.has_perm('myapp.can_update_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"update\"'"
    elif(sqltype=='delete'):
        if request.user.has_perm('myapp.can_delete_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"delete\"'"
    elif(sqltype=='truncate'):
        if request.user.has_perm('myapp.can_truncate_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"truncate\"'"
    elif(sqltype=='create'):
        if request.user.has_perm('myapp.can_create_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"create\"'"
    elif(sqltype=='drop'):
        if request.user.has_perm('myapp.can_drop_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"drop\"'"
    elif (sqltype == 'alter' or sqltype == 'rename'):
        if request.user.has_perm('myapp.can_alter_mysql'):
            return sqltext
        else:
            return "select 'Don\\'t have permission to \"alter\"'"
    else:
        return wrong_msg



def run_mysql_exec(hosttag,sql,useraccount,request):
    #确认dbname
    a = Db_name.objects.filter(dbtag=hosttag)[0]
    #a = Db_name.objects.get(dbtag=hosttag)
    tar_dbname = a.dbname
    if (not cmp(sql,wrong_msg)):
        results,col = mysql_query(wrong_msg,user,passwd,host,int(port),dbname)
        return results,col,tar_dbname
    #如果instance中有备库role='write'，则选择从主库读取
    try:
        if a.instance.all().filter(role='write')[0]:
            tar_host = a.instance.all().filter(role='write')[0].ip
            tar_port = a.instance.all().filter(role='write')[0].port
    #如果没有设置或没有role=write，则选择第一个role=all的库读取
    except Exception,e:
        try:
            tar_host = a.instance.all().filter(role='all')[0].ip
            tar_port = a.instance.all().filter(role='all')[0].port
        except Exception,e:
            #没有找到role为all或者write的实例配置
            wrongmsg = "select \"" +str(e).replace('"',"\"")+"\""
            results,col = mysql_query(wrongmsg,user,passwd,host,int(port),dbname)
            return results,col,tar_dbname
    pc = prpcrypt()
    #find the useraccount and passwd for the user
    for i in a.db_account_set.all():
        if i.role != 'read' and i.role != 'admin':
            #find the specified account for the user
            if i.account.all().filter(username=useraccount):
                tar_username = i.user
                tar_passwd = pc.decrypt(i.passwd)
                break
    #not find specified account for the user ,specified the public account to the user
    if not vars().has_key('tar_username'):
        for i in a.db_account_set.all():
            if i.role != 'read' and i.role != 'admin':
                # find the specified account for the user
                if i.account.all().filter(username=public_user):
                    tar_username = i.user
                    tar_passwd = pc.decrypt(i.passwd)
                    break
    try:
        #之前根据check_mysql_exec判断过权限，如果是select则说明没权限，不记录日志
        if (sql.split()[0]!='select'):
            log_mysql_op(useraccount,sql,tar_dbname,hosttag,request)
            results,col = mysql_exec(sql,tar_username,tar_passwd,tar_host,tar_port,tar_dbname)
        else:
            results,col = mysql_query(sql,user,passwd,host,int(port),dbname)
    except Exception, e:
        #防止库连不上,返回一个wrong_message
        results,col = ([str(e)],''),['error']
    return results,col,tar_dbname



def mysql_exec(sql,user=user,passwd=passwd,host=host,port=int(port),dbname=dbname):
    try:
        conn=MySQLdb.connect(host=host,user=user,passwd=passwd,port=int(port),connect_timeout=5,charset='utf8')
        conn.select_db(dbname)
        curs = conn.cursor()
        result=curs.execute(sql)
        conn.commit()
        curs.close()
        conn.close()
        return (['影响行数: '+str(result)],''),['success']
    except Exception,e:
        if str(e)=='(2014, "Commands out of sync; you can\'t run this command now")':
            return (['只能输入单条sql语句'],''),['error']
        else:
            return([str(e)],''),['error']


def get_pre(dbtag):
    db = Db_name.objects.get(dbtag=dbtag)
    ins = db.instance.all()
    acc = db.account.all()
    acc_list = Db_account.objects.filter(dbname=db)
    gp = db.db_group_set.all()
    '''print db.instance.all().query
    print db.account.all().query
    print Db_account.objects.filter(dbname=db).query
    print db.db_group_set.all().query'''

    return acc_list,ins,acc,gp

def get_user_pre(username,request):
    if len(username)<=30:
        try :
            info = "PRIVILEGES FOR " + username
            dblist = User.objects.get(username=username).db_name_set.all()
        except :
            info = "PLEASE CHECK YOUR INPUT"
            dblist = User.objects.get(username=request.user.username).db_name_set.all()
    else:
        info = "INPUT TOO LONG"
        dblist = User.objects.get(username=request.user.username).db_name_set.all()
    return dblist,info

#used in prequery.html
def get_groupdb(group):
    grouplist = Db_group.objects.filter(groupname=group)
    return grouplist

#used in prequery.html
def get_privileges(username):
    pri = User.objects.get(username=username).user_permissions.all()
    return pri

def get_UserAndGroup():
    user_list = User.objects.exclude(username=public_user).order_by('username')
    group_list = Db_group.objects.all().order_by('groupname')
    # for row in User.objects.all():
    #     user_list.append(row.username)
    return user_list,group_list


def get_UserList():
    user_list = User.objects.exclude(username=public_user).order_by('username')
    # for row in User.objects.all():
    #     user_list.append(row.username)
    return user_list


def get_user_grouppri(username):
    user = User.objects.get(username=username)
    a = user.db_group_set.all()
    b = user.groups.all()
    return  a,b

def clear_userpri(username):
    user = User.objects.get(username=username)
    for i in Db_name.objects.all():
        i.account.remove(user)
    for i in Db_group.objects.all():
        i.account.remove(user)
    user.user_permissions.clear()
    user.groups.clear()

def set_groupdb(username,li):
    user = User.objects.get(username=username)
    tag_list=[]
    for i in li:
        tmp_gp = Db_group.objects.get(id=i)
        try:
            tmp_gp.account.add(user)
        except Exception,e:
            pass

        for x in tmp_gp.dbname.all():
            tag_list.append(x.dbtag)
            try:
                x.account.add(user)
            except Exception,e:
                pass
    tag_list = list(set(tag_list))
    return tag_list

#create user in pre_set.html
def create_user(username,passwd,mail):
    if len(username)>0 and len(passwd)>0 and len(mail)>0:
        user = User.objects.create_user(username=username,password=passwd,email=mail)
        user.save()
    return user
#delete user in pre_set.html
def delete_user(username):
    user = User.objects.get(username=username)
    user.delete()

#user dbtaglist and user to set user-db relation
def set_user_db(user,dblist):
    setdblist = Db_name.objects.filter(dbtag__in=dblist)
    for i in setdblist:
        try:
            i.account.add(user)
            i.save()
        except Exception,e:
            pass

# a = Permission.objects.filter(codename__istartswith='can')


def set_usergroup(user,group):
    # user.groups.clear()
    grouplist = Group.objects.filter(name__in=group)
    for i in grouplist:
        try:
            user.groups.add(i)
            user.save()
        except Exception,e:
            pass
    # for i in a:
    #     print i.codename

def get_usergp_list():
    # perlist = Permission.objects.filter(codename__istartswith='can')
    grouplist = Group.objects.all().order_by('name')
    return grouplist

def get_diff(dbtag1,tb1,dbtag2,tb2):

    if os.path.isfile(path_mysqldiff) :
        tar_host1, tar_port1, tar_username1, tar_passwd1,tar_dbname1 = get_conn_info(dbtag1)
        tar_host2, tar_port2, tar_username2, tar_passwd2,tar_dbname2 = get_conn_info(dbtag2)

        server1 = ' -q --server1={}:{}@{}:{}'.format(tar_username1,tar_passwd1,tar_host1,str(tar_port1))
        server2 = ' --server2={}:{}@{}:{}'.format(tar_username2,tar_passwd2,tar_host2,str(tar_port2))
        option = ' --difftype=sql'
        table = ' {}.{}:{}.{}'.format(tar_dbname1,tb1,tar_dbname2,tb2)
        cmd = path_mysqldiff + server1 + server2 + option + table
        output = os.popen(cmd)
        result = output.read()
        # result = commands.getoutput(cmd)
    else :
        result = "mysqldiff not installed"

    return result

def get_conn_info(hosttag):
    a = Db_name.objects.filter(dbtag=hosttag)[0]
    #a = Db_name.objects.get(dbtag=hosttag)
    tar_dbname = a.dbname
    #如果instance中有备库role='read'，则选择从备库读取
    try:
        if a.instance.all().filter(role='read')[0]:
            tar_host = a.instance.all().filter(role='read')[0].ip
            tar_port = a.instance.all().filter(role='read')[0].port
    #如果没有设置或没有role=read，则选择第一个读到的实例读取
    except Exception,e:
        tar_host = a.instance.filter(role__in=['write','all'])[0].ip
        tar_port = a.instance.filter(role__in=['write','all'])[0].port
    pc = prpcrypt()
    for i in a.db_account_set.all():
        if i.role == 'admin':
            tar_username = i.user
            tar_passwd = pc.decrypt(i.passwd)
            break
    return tar_host,tar_port,tar_username,tar_passwd,tar_dbname
#定时收集mysql的数据和监控
def get_mysql_hosts_list(ipaddr):
    if len(ipaddr)>0:
        datalist = mysql_hosts.objects.filter(hosts_ip__contains=ipaddr).order_by("-dtime")[0:100]
    else:
        datalist = mysql_hosts.objects.all().order_by("-dtime")[0:100]
    return datalist

def get_mysql_hosts_list_run(status ):
    if len(status)>0:
        datalist = mysql_hosts.objects.filter(host_status=status).order_by("-dtime")[0:100]
    else:
        datalist = mysql_hosts.objects.all().order_by("-dtime")[0:100]
    return datalist
def add_mysql_hosts(host_ip,host_port,host_user,host_pwd,host_status,dtime):
    pc = prpcrypt()
    host_pwd = pc.encrypt(host_pwd)
    host = mysql_hosts(hosts_ip=host_ip,host_port=host_port,host_user=host_user,host_pwd=host_pwd,host_status=host_status,dtime=dtime)
    host.save()

def modify_mysql_hosts(id,host_port,host_user,host_pwd,host_status,dtime):
    if len(id)>0:
        pc = prpcrypt()
        host_pwd = pc.decrypt(host_pwd)
        host_pwd = pc.encrypt(host_pwd)
        obj = mysql_hosts.objects.get(id=id)
        obj.host_port = host_port
        obj.host_user = host_user
        obj.host_pwd = host_pwd
        obj.host_status = host_status
        obj.dtime=dtime
        obj.save()
def delete_mysql_hosts(id):
    host = mysql_hosts.objects.get(id=id)
    host.delete()
#20180524 by yuerl
def add_mysql_db_diff(row_number,stype,host0,item0,host1,item1,result,dbtime):
        mysql_db_save = mysql_dbcompare(row_number=row_number,stype=stype,host0=host0,item0=item0,host1=host1,item1=item1,result=result,dbtime=dbtime)
        mysql_db_save.save()


def delete_all_mysql_db_diff(choosed_host0,choosed_host1):
    mysql_db_save = mysql_dbcompare.objects.filter(host0=choosed_host0).filter(host1=choosed_host1).delete()
    # mysql_db_save.save()

def get_all_mysql_db_diff(choosed_host0,choosed_host1):
    datalist = mysql_dbcompare.objects.filter(host0=choosed_host0).filter(host1=choosed_host1)
    return datalist


#20180604
def get_main_chart(flag):
    with connection.cursor() as cursor:
        sql=""
        if flag == 1:
            sql = "select  concat(DATE_FORMAT(a.`create_time`,'%Y-%m-%H'),'T00:00:00') sdate,count(1) scount from myapp_oper_log a\
                  where a.`create_time`> date_sub(now(),interval 7 day)\
                  group by  concat(DATE_FORMAT(a.`create_time`,'%Y-%m-%H'),'T00:00:00')  order by CONCAT(DATE_FORMAT(a.`create_time`,'%Y-%m-%H'),'T00:00:00')"
        elif flag == 0:
            sql = "SELECT sdate,COUNT(1) scount FROM (\
                  SELECT  CONCAT(DATE_FORMAT(a.`create_time`,'%Y-%m-%H'),'T00:00:00') sdate,a.`dbtag` FROM myapp_oper_log a\
                WHERE a.`create_time`> DATE_SUB(NOW(),INTERVAL 7 DAY)\
                GROUP BY  CONCAT(DATE_FORMAT(a.`create_time`,'%Y-%m-%H'),'T00:00:00'),a.`dbtag`  ORDER BY CONCAT(DATE_FORMAT(a.`create_time`,'%Y-%m-%H'),'T00:00:00')\
                )temp GROUP BY sdate ORDER BY sdate"
        row = cursor.execute(sql)
        result = cursor.fetchmany(size=7)
        cursor.close()
    return result

    return mysql_query(sql, func.user, func.passwd, func.host, int(func.port), func.dbname)



#mysql monitor
def mysql_dashbord_query_space():
    with connection.cursor() as cursor:
        sql_str="SELECT aa.hosts_ip,aa.table_schema,aa.table_name,aa.table_rows, DATE_FORMAT(aa.dtime,'%Y-%m-%d %H')  FROM (SELECT *  FROM  myapp_mysql_check_space a \
WHERE a.`dtime` BETWEEN STR_TO_DATE(CONCAT(DATE_FORMAT(NOW(),'%Y-%m-%d'),' 00:00:00'),'%Y-%m-%d %H:%i:%s') AND STR_TO_DATE(CONCAT(DATE_FORMAT(NOW(),'%Y-%m-%d'),' 23:59:59'),'%Y-%m-%d %H:%i:%s') )aa \
JOIN ( SELECT a.hosts_ip,a.table_schema,a.table_name ,MAX(table_rows),MIN(table_rows) FROM  myapp_mysql_check_space a \
WHERE a.`dtime` BETWEEN STR_TO_DATE(CONCAT(DATE_FORMAT(NOW(),'%Y-%m-%d'),' 00:00:00'),'%Y-%m-%d %H:%i:%s') AND STR_TO_DATE(CONCAT(DATE_FORMAT(NOW(),'%Y-%m-%d'),' 23:59:59'),'%Y-%m-%d %H:%i:%s') \
 GROUP BY a.hosts_ip,a.table_schema,a.table_name LIMIT 0,5) bb ON aa.hosts_ip=bb.hosts_ip AND aa.table_schema=bb.table_schema AND aa.table_name=bb.table_name\
 ORDER BY aa.hosts_ip,aa.table_schema,aa.table_name, DATE_FORMAT(aa.dtime,'%Y-%m-%d %H')"
        count=cursor.execute(sql_str)
        index = cursor.description
        col = []
        # get column name
        for i in index:
            col.append(i[0])
        result = cursor.fetchall()



        cursor.close()
    return (result, col)

def mysql_get_blacklist(username):
    with connection.cursor() as cursor:
        sql_str="SELECT a.`id`,a.`dbtag`,a.`tbname`,c.`id` userid ,c.`username` FROM tb_blacklist a JOIN tb_blacklist_user_permit b ON a.`id`=b.tb_blacklist_id"
        sql_str = sql_str + "  JOIN auth_user c ON c.`id`=b.`user_id`  "
        if len(username)>0:
            sql_str = sql_str + "  WHERE c.`username`=%s "
            cursor.execute(sql_str, [username])
            row = cursor.fetchall()
        else:
            cursor.execute(sql_str)
            row=cursor.fetchall()
    cursor.close()
    return row

def mysql_blacklist_tb(sql,username,dbtag):
    with connection.cursor() as cursor:
        sql_str="SELECT a.`id`,a.`dbtag`,a.`tbname`,c.`id` userid ,c.`username` FROM tb_blacklist a JOIN tb_blacklist_user_permit b ON a.`id`=b.tb_blacklist_id"
        sql_str = sql_str + "  JOIN auth_user c ON c.`id`=b.`user_id`  "
        sql_str = sql_str + "  WHERE c.`username`=%s  and a.`dbtag`=%s"
        cursor.execute(sql_str, [username,dbtag])
        row = cursor.fetchall()
        if len(row)>0:
            list_data=list(row)
            tbnames= str(list_data[0][2]).split(',')
            sql_upper=str(sql).upper().replace(";","")
            if str(sql_upper).find("FROM")>0:
                sfrom=str(sql_upper).index("FROM")
                sql_upper = sql_upper[sfrom:]
                swhere = str(sql_upper).find("WHERE")
                if swhere > 0:
                    sql_upper = sql_upper[0:swhere]
                else:
                    sql_upper = sql_upper

                list_a = str(sql_upper).split(',')
                list_b = str(sql_upper).split()
                for tb in tbnames:
                    for i in list_a:
                        if i == tb.upper():
                            return 1, tb
                    for i in list_b:
                        if i == tb.upper():
                            return 1, tb
            else:
                return 0, ""
    cursor.close()
    return 0, ""


#插入
def mysql_insert_blacklist(username,dbtag,tablename):
    with connection.cursor() as cursor:
        row=0
        sql_str00="SELECT count(1) FROM tb_blacklist a JOIN tb_blacklist_user_permit b ON a.`id`=b.tb_blacklist_id JOIN auth_user c ON c.`id`=b.`user_id`  where  c.`username`=%s"
        cursor.execute(sql_str00, [username])
        count=cursor.fetchall()
        if count[0][0]==0:
            sql_str0="INSERT INTO tb_blacklist(dbtag,tbname)VALUES(%s,%s)"
            sql_str1 = "INSERT INTO tb_blacklist_user_permit(tb_blacklist_id,user_id) SELECT %s,id FROM auth_user WHERE `username`=%s"
            if len(username)>0 and len(dbtag)>0 and len(tablename)>0:
                cursor.execute(sql_str0, [dbtag,tablename])
                permit_id=int(cursor.lastrowid)
                row =cursor.execute(sql_str1, [permit_id, username])
    return row


def mysql_modify_blacklist(username,dbtag,tablename):
    with connection.cursor() as cursor:
        row=0
        sql_str00="SELECT a.id FROM tb_blacklist a JOIN tb_blacklist_user_permit b ON a.`id`=b.tb_blacklist_id JOIN auth_user c ON c.`id`=b.`user_id`  where  c.`username`=%s and a.`dbtag`=%s"
        cursor.execute(sql_str00, [username,dbtag])
        aid=cursor.fetchall()
        if aid is not None :
            sql_str0="UPDATE tb_blacklist SET tbname=CONCAT(REPLACE(REPLACE(tbname,%s,''),%s,''),',',%s)  WHERE id=%s"
            if len(username)>0 and len(dbtag)>0 and len(tablename)>0:
                s1=','+tablename
                s2=tablename+','
                row=cursor.execute(sql_str0, [s1,s2,tablename,aid[0][0]])
    return row

def mysql_delete_blacklist(username,dbtag,tablename):
    with connection.cursor() as cursor:
        row=0
        sql_str00="SELECT a.id FROM tb_blacklist a JOIN tb_blacklist_user_permit b ON a.`id`=b.tb_blacklist_id JOIN auth_user c ON c.`id`=b.`user_id`  where  c.`username`=%s and a.`dbtag`=%s"
        cursor.execute(sql_str00, [username,dbtag])
        aid=cursor.fetchall()
        if aid is not None:
            sql_str0="UPDATE tb_blacklist SET tbname=REPLACE(REPLACE(tbname,%s,''),%s,'')  WHERE id=%s"
            if len(username)>0 and len(dbtag)>0 and len(tablename)>0:
                s1=','+tablename
                s2=tablename+','
                row=cursor.execute(sql_str0, [s1,s2,aid[0][0]])
    return row

#用户资料查询
def mysql_user_detail_list(username):
    with connection.cursor() as cursor:
        sql_str="SELECT a.`id`,a.`user`,b.`username`,a.real_name,a.position,a.`telephone`,a.`wechart`,a.`create_time` FROM myapp_user_detail a JOIN auth_user b on a.`user`=b.`id`"
        if len(username)>0:
            sql_str = sql_str + "  WHERE b.`username` like   %s  order by a.`create_time` desc "
            cursor.execute(sql_str, ["%"+str(username)+"%"])
            row = cursor.fetchall()
        else:
            cursor.execute(sql_str)
            row=cursor.fetchall()
    cursor.close()
    return row

def mysql_user_detail_modify(id,position,telephone,wechart,real_name):
        obj = User_detail.objects.get(id=id)
        if len(position)>0:
          obj.position=  position
        if len(telephone)>0:
          obj.telephone=  telephone
        if len(wechart)>0:
          obj.wechart=  wechart
        if len(real_name)>0:
          obj.real_name=  real_name
        obj.save()

def mysql_user_detail_chk(username):
    with connection.cursor() as cursor:
        sql_str="SELECT count(1) from myapp_user_detail a join auth_user b on a.`user`=b.`id` WHERE b.`username` = %s "
        cursor.execute(sql_str,[username])
        row = cursor.fetchall()
    cursor.close()
    return row

def mysql_user_detail_save(username,position,telephone,wechart,real_name):
    with connection.cursor() as cursor:
        sql_str="INSERT INTO  myapp_user_detail(user,position,telephone,wechart,create_time,real_name) SELECT a.`id`,%s,%s,%s,NOW(),%s FROM auth_user a WHERE a.username=%s "
        cursor.execute(sql_str,[position,telephone,wechart,real_name,username])
        row = cursor.fetchall()
    cursor.close()
    return row


def static_failed_task(mins):
    with connection.cursor() as cursor:
        sql_str="SELECT  c.`wechart`,a.`operator`,COUNT(1) FROM myapp_task a JOIN auth_user b ON a.`operator`=b.`username`  JOIN myapp_user_detail c ON c.`user`=b.`id` WHERE  a.`status`='executed failed' AND a.`create_time`> DATE_ADD(NOW(), INTERVAL - %s MINUTE) GROUP BY a.`operator` "
        cursor.execute(sql_str,[mins])
        index = cursor.description
        col = []
        for i in index:
            col.append(i[0])
        row = cursor.fetchall()
    cursor.close()
    return col,row

def main():
    return 1
if __name__=='__main__':
    main()
