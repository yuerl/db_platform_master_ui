# -*- coding: utf-8 -*-
import sys,uuid
reload(sys)
sys.setdefaultencoding('utf-8')
import MySQLdb,sys,string,time,datetime,uuid,pymongo,json,cx_Oracle,os
from django.contrib.auth.models import User
from myapp.models import Db_name,Db_account,Db_instance
from myapp.etc import config
from django.core.serializers.json import DjangoJSONEncoder
from myapp.models import Oper_log
from myapp.include.encrypt import prpcrypt
import inception_oracle
select_limit = int(config.select_limit)
export_limit = int(config.export_limit)
wrong_msg = config.wrong_msg
public_user = config.public_user
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.AL32UTF8'
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
#记录用户所有操作
def log_oracle_op(user,sqltext,mydbname,dbtag,ipaddr):
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
    log = Oper_log (user=username,sqltext=sqltext,sqltype=sqltype,login_time=lastlogin,create_time=create_time,dbname=mydbname,dbtag=dbtag,ipaddr=ipaddr)
    log.save()
    return 1

#获取下拉菜单列表
def get_oracle_hostlist(username,tag='tag',search=''):
    dbtype='Oracle'
    host_list = []
    if len(search) ==0:
        if (tag=='tag'):
            a = User.objects.get(username=username)
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

#检查输入语句,并返回行限制数
def check_oracle_query(sqltext,user,type='select'):
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
    limit = ' ) where rownum <= '+ num

    sqltext = sqltext.strip()
    sqltype = sqltext.split()[0].lower()
    list_type = ['select','explain plan for']
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
    # try:
    #     has_limit = cmp(sqltext.split()[-2].lower(),'limit')
    # except Exception,e:
    #     #prevent some input like '1' or 'ss' ...
    #     return wrong_msg, num

    for i in list_type:
        if (not cmp(i,sqltype)):
            flag=1
            break
    if (flag==1):
        if (sqltype =='select' ):
            return "select * from ("+sqltext+limit,num
    else:
        return wrong_msg,num

def check_explain (sqltext):
    sqltext = sqltext.strip()
    sqltype = sqltext.split()[0].lower()
    if (sqltype =='select'):
        sqltext = 'explain plan for  '+sqltext
        return sqltext
    else:
        return wrong_msg
#执行oracle的查询
def oracle_query(sql,user,passwd,host,port,dbname,limitnum=select_limit):
    try:
	    #conn = cx_Oracle.connect(host=host, user=user, passwd=passwd, port=int(port), connect_timeout=5, charset='utf8')
        # conn=cx_Oracle.connect('/密码@主机ip地址/orcl')
        conn = cx_Oracle.connect(user,passwd,host+':'+port+'/'+dbname)
        cursor = conn.cursor()
        count=cursor.execute(sql)
        index=cursor.description
        col=[]
        #get column name
        for i in index:
            col.append(i[0])
        #result=cursor.fetchall()
        # result=cursor.fetchmany(size=int(limitnum))
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return (result,col)
    except Exception,e:
        return([str(e)],''),['error']

#执行计划专用
def oracle_explain_query(sql,user,passwd,host,port,dbname):
    try:
	    #conn = cx_Oracle.connect(host=host, user=user, passwd=passwd, port=int(port), connect_timeout=5, charset='utf8')
        # conn=cx_Oracle.connect('/密码@主机ip地址/orcl')
        conn = cx_Oracle.connect(user,passwd,host+':'+port+'/'+dbname)
        cursor = conn.cursor()
        cursor.execute(sql)
        cursor.execute("select * from table(dbms_xplan.display)")
        index=cursor.description
        col=[]
        #get column name
        for i in index:
            col.append(i[0])
        #result=cursor.fetchall()
        # result=cursor.fetchmany(size=int(limitnum))
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return (result,col)
    except Exception,e:
        return([str(e)],''),['error']

#执行oracle的语句异步任务使用
def oracle_run(sql,user,passwd,host,port,dbname):
    try:
	    #conn = cx_Oracle.connect(host=host, user=user, passwd=passwd, port=int(port), connect_timeout=5, charset='utf8')
        # conn=cx_Oracle.connect('/密码@主机ip地址/orcl')
        conn = cx_Oracle.connect(user,passwd,host+':'+port+'/'+dbname)
        cursor = conn.cursor()
        # count=cursor.execute(sql)
        # cursor.commit()
        #多次提交，每个分号码都要提交一次
        sum_count=0
        current_milli_time = lambda: int(round(time.time() * 1000))
        str_crent_time=str(current_milli_time())
        str_sequence=str_crent_time[0:10]+"_"+str_crent_time[10:]+"_"
        sql_list=str(sql).split(';')
        result= []
        long_increase=1
        backup_host = str(host).replace('.', '_') + '_' + str(port) + '_' + str(user).lower()
        if len(sql_list)>0:
            for i in range(len(sql_list)):
                time_begin = datetime.datetime.now()
                if len(str(sql_list[i]).replace('\r','').replace('\n','').strip())>0:
                    exec_backup='Execute failed'
                    success_flag='failed'
                    rowaffect=0
                    try:
                        ################################################################
                        try:
                            inception_oracle.backupdb_check_db(user, passwd, host, port, dbname)
                            undosql_list,table_name,sql_type=inception_oracle.backupdml_insert(str(sql_list[i]).encode('utf8'),user,passwd,host,port,dbname)
                            for p in range(len(undosql_list)):
                                success_flag,row_incr=inception_oracle.backupdb_check_table(user, passwd, host, port, dbname, table_name,undosql_list[p],str_sequence+str(long_increase),str(sql_list[i]).encode('utf8'),sql_type)
                                rowaffect = rowaffect + row_incr
                        except Exception, e:
                            continue
                        ################################################################

                        count = cursor.execute(str(sql_list[i]).encode('utf8'))
                        if count is not None:
                            sum_count = sum_count + count
                        conn.commit()
                        exec_backup = 'Execute Successfully'
                        time_end = datetime.datetime.now()
                        run_time = str((time_end - time_begin).seconds)
                        if success_flag=='success':
                            exec_backup=exec_backup+'Backup successfully'
                        else:
                            exec_backup = exec_backup + 'Backup failed'
                        temp_item=(long_increase,'EXECUTED',0,exec_backup,'None',str(sql_list[i]).encode('utf8'),rowaffect,"'"+str_sequence+str(long_increase)+"'",backup_host,run_time,'')
                        result.append(temp_item)
                    except Exception, e:
                        time_end = datetime.datetime.now()
                        run_time=str((time_end - time_begin).seconds)
                        temp_item = (long_increase, 'EXECUTED', 2,'Execute failed', str(e),str(sql_list[i]).encode('utf8'),rowaffect,"'"+str_sequence+str(long_increase)+"'",backup_host,run_time,'')
                        result.append(temp_item)
                        continue
                    long_increase=long_increase+1

        # conn = cx_Oracle.connect('load/123456@loaclhost/ora11g')
        # c = conn.cursor()
        # x = c.execute('insert into demo(v) values(:1)', ['nice'])
        # conn.commit();
        # c.close()
        # conn.close()
        # index=cursor.description
        # col=[]
        # #get column name
        # for i in index:
        #     col.append(i[0])
        # result = cursor.fetchall()
        cursor.close()
        conn.close()
        col=['ID', 'stage', 'errlevel', 'stagestatus', 'errormessage', 'SQL', 'Affected_rows', 'sequence', 'backup_dbname', 'execute_time', 'sqlsha1']
        return (list(result),col)
    except Exception,e:
        return([str(e)],''),['error']



def get_oracle_data(hosttag,sql,useraccount,request,limitnum):
    ipaddr=get_client_ip(request)
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
            log_oracle_op(useraccount,sql,tar_dbname,hosttag,ipaddr)
        results,col = oracle_query(sql,tar_username,tar_passwd,tar_host,tar_port,tar_dbname,limitnum)
    except Exception, e:
        #防止日志库记录失败，返回一个wrong_message
        results,col = ([str(e)],''),['error']
        #results,col = mysql_query(wrong_msg,user,passwd,host,int(port),dbname)
    return results,col,tar_dbname

#执行oracle的语句异步任务使用
def incept_oracle_run(hosttag,sql,useraccount,ipaddr):
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
            log_oracle_op(useraccount,sql,tar_dbname,hosttag,ipaddr)
        #inception_oracle.backupdb_check(tar_username,tar_passwd,tar_host,tar_port,tar_dbname)
        results,col = oracle_run(sql,tar_username,tar_passwd,tar_host,tar_port,tar_dbname)
    except Exception, e:
        #防止日志库记录失败，返回一个wrong_message
        results,col = ([str(e)],''),['error']
        #results,col = mysql_query(wrong_msg,user,passwd,host,int(port),dbname)
    return results,col,tar_dbname

def get_oracle_explain_data(hosttag,sql,useraccount,request,limitnum):
    ipaddr = get_client_ip(request)
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
            log_oracle_op(useraccount,sql,tar_dbname,hosttag,ipaddr)
        sql=str(sql).replace(';','')
        results, col = oracle_explain_query(sql, tar_username, tar_passwd, tar_host, tar_port, tar_dbname)
        #results,col = oracle_query("select * from table(dbms_xplan.display)",tar_username,tar_passwd,tar_host,tar_port,tar_dbname,limitnum)

    except Exception, e:
        #防止日志库记录失败，返回一个wrong_message
        results,col = ([str(e)],''),['error']
        #results,col = mysql_query(wrong_msg,user,passwd,host,int(port),dbname)
    return results,col,tar_dbname


def check_oracle_exec(sqltext,request):
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

def oracle_exec(sql, user, passwd, host, port, dbname):
    try:
        conn = cx_Oracle.connect(user, passwd, host + ':' + port + '/' + dbname)
        #conn.select_db(dbname)
        curs = conn.cursor()
        sum_count = 0
        sql_list = str(sql).split(';')
        if len(sql_list) > 0:
            for i in range(len(sql_list)):
                if len(str(sql_list[i]).replace('\r', '').replace('\n', '').strip()) > 0:
                    count = curs.execute(str(sql_list[i]).encode('utf8'))
                    if count is not None:
                        sum_count = sum_count + count
                    conn.commit()
        curs.close()
        conn.close()
        return (['影响行数: '+str(sum_count)],''),['success']
    except Exception,e:
        if str(e)=='(2014, "Commands out of sync; you can\'t run this command now")':
            return (['只能输入单条sql语句'],''),['error']
        else:
            return([str(e)],''),['error']


def run_orcle_exec(hosttag,sql,useraccount,request):
    ipaddr = get_client_ip(request)
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
    if (not cmp(sql,wrong_msg)):
        results,col = oracle_query(wrong_msg,useraccount,tar_passwd,tar_host,int(tar_port),tar_dbname)
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
            results,col = oracle_query(wrongmsg,useraccount,tar_passwd,tar_host,int(tar_port),tar_dbname)
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
            log_oracle_op(useraccount,sql,tar_dbname,hosttag,ipaddr)
            results,col = oracle_exec(sql,tar_username,tar_passwd,tar_host,tar_port,tar_dbname)
        else:
            results,col = oracle_query(sql,tar_username,tar_passwd,tar_host,int(tar_port),tar_dbname)
    except Exception, e:
        #防止库连不上,返回一个wrong_message
        results,col = ([str(e)],''),['error']
    return results,col,tar_dbname


if __name__ == '__main__':
 print("123312")