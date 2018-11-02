#!/usr/bin/python
#_*_coding:utf-8 _*_
import os
import datetime
from optparse import OptionParser
import urllib,urllib2
import threading
import json
import sys
import simplejson
import os
from myapp.include import function as func
from myapp.include.encrypt import prpcrypt
from myapp.models import mysql_hosts,mysql_check,mysql_check_command,mysql_check_space
from myapp.include import mysql_func
reload(sys)
sys.setdefaultencoding('utf-8')
# '''https://work.weixin.qq.com/wework_admin/frame#contacts'''
def gettoken(corpid,corpsecret):
    gettoken_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + corpid + '&corpsecret=' + corpsecret
    print gettoken_url
    try:
        token_file = urllib2.urlopen(gettoken_url)
    except urllib2.HTTPError as e:
        print e.code
        print e.read().decode("utf8")
        sys.exit()
    token_data = token_file.read().decode('utf-8')
    token_json = json.loads(token_data)
    token_json.keys()
    token = token_json['access_token']
    return token
def wxsenddata(user,subject,content):
    corpid = 'wwd1cb83bb19c4c675'
    #CorpID是企业号的标识
    corpsecret = 'YHQeUQZfBeI_QN-V-1WRrq01awIcXpTIW2lc62Aqh8Q'
    #corpsecretSecret是管理组凭证密钥
    accesstoken = gettoken(corpid,corpsecret)
    send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + accesstoken
    users=user.split(',')
    for u in users:
        send_values = {
        "touser":u, #企业号中的用户帐号，在zabbix用户Media中配置，如果配置不正常，将按部门发送。
        #"toparty":"1", #企业号中的部门id。
        "msgtype":"text", #消息类型。
        "agentid":"1000002", #企业号中的应用id。
        "text":{
        "content":subject + '\n' + content
        },"safe":"0"
        }
# send_data = json.dumps(send_values, ensure_ascii=False)
        send_data = simplejson.dumps(send_values, ensure_ascii=False).encode('utf-8')
        send_request = urllib2.Request(send_url, send_data)
        response = json.loads(urllib2.urlopen(send_request).read())


# hosts_ip = models.CharField(max_length=35)
# chk_type = models.CharField(max_length=35)
# chk_status = models.CharField(max_length=20)
# msg = models.CharField(max_length=500)
# dtime = models.DateTimeField(db_index=True)

def add_mysql_check(host_ip,chk_type,chk_status,msg):
    dtime=str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    host = mysql_check(hosts_ip=host_ip,chk_type=chk_type,chk_status=chk_status,msg=msg,dtime=dtime)
    host.save()

def add_mysql_check_command(host_ip, command,state,count):
        dtime = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        host = mysql_check_command(hosts_ip=host_ip, command=command, state=state, count=count, dtime=dtime)
        host.save()

def add_mysql_check_space(host_ip,table_schema ,table_name,table_rows,data_length):
    dtime = str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    host = mysql_check_space(hosts_ip=host_ip, table_schema=table_schema,table_name=table_name,table_rows=table_rows,data_length=data_length, dtime=dtime)
    host.save()

def chk_mysqlping(host_ip,host_port,host_user,host_pwd):
    host = (host_ip,str(func.mysql_bin)+'mysqladmin -u'+host_user+' -p'+host_pwd+' -P'+str(host_port)+'  -h'+host_ip+' ping')
    items = [('mysqld','is alive')]
    flag = 0;
    try:
        p = os.popen(host[1])
        for line in p.readlines():
             for item in items:
                 if line.find(item[0]) > -1:
                     if line.find(item[1]) > -1:
                       flag=1;
                       add_mysql_check(host_ip, "chk_mysqlping", "normal", "mysqld is alive")
        if flag == 0:
            # error
            add_mysql_check(host_ip, "chk_mysqlping", "error", "mysqld is unreachable")
            # wxsenddata('YueRenLiang', '【' + host[0] + '】', '[mysqld is unreachable]')
    except Exception, e:
            flag=-1
            add_mysql_check(host_ip, "chk_mysqlping", "exception", "chk_mysqlping out exception")
            # wxsenddata('YueRenLiang', 'MYSQL chk_mysqlping', '【TIME】:' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + '\r\n' + '【TYPE】:high' + '\r\n'
            #          + '【IP】' + host[0] + '\r\n' + '【MSG】:chk_mysqlping not  available')
    finally:
            return flag
#线程连接数
def chk_mysql_threads_connected(host_ip,host_port,host_user,host_pwd):
    host = (host_ip,str(func.mysql_bin)+'mysql -u'+host_user+' -p'+host_pwd+' -P'+str(host_port)+' -h'+host_ip+' -e "show status like \'Threads_connected\'"')
    items = [('Threads_connected')]
    flag = 0;
    try:
        p = os.popen(host[1])
        for line in p.readlines():
             #line=line.decode('cp936').encode('utf-8')
             for item in items:
                 if line.find(item[0]) > -1:
                     flag = 1;
                     add_mysql_check(host_ip, "chk_mysql_threads_connected", "normal", line.replace('\t','').replace('Threads_connected','').replace("\n", ""))
        if flag == 0:
            # error
            add_mysql_check(host_ip, "chk_mysql_threads_connected", "error", "chk_mysql_threads_connected is unreachable")
            # wxsenddata('YueRenLiang', '【' + host[0] + '】', '[chk_mysql_threads_connected is unreachable]')

    except Exception, e:
        flag = -1
        add_mysql_check(host_ip, "chk_mysql_threads_connected", "exception", "chk_mysql_threads_connected out exception")
        # wxsenddata('YueRenLiang', 'MYSQL chk_mysql_threads_connected', '【TIME】:' + str(
        #     datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + '\r\n' + '【TYPE】:high' + '\r\n'
        #            + '【IP】' + host[0] + '\r\n' + '【MSG】:chk_mysql_threads_connected not  available')
#线程运行数
def chk_mysql_threads_running(host_ip,host_port,host_user,host_pwd):
    host = (host_ip, str(func.mysql_bin)+'mysql -u' + host_user + ' -p' + host_pwd + ' -P' + str(
        host_port) + ' -h' + host_ip + ' -e "show status like \'Threads_running\'"')
    items = [('Threads_running')]
    flag = 0;
    try:
        p = os.popen(host[1])
        for line in p.readlines():
             line=line.decode('cp936').encode('utf-8')
             for item in items:
                 if line.find(item[0]) > -1:
                     add_mysql_check(host_ip, "Threads_running", "normal",
                                     line.replace('\t', '').replace('Threads_running', '').replace("\n", ""))
                     flag=1
        if flag==0:
            add_mysql_check(host_ip, "Threads_running", "error","chk_mysql_threads_connected is unreachable")
    except Exception, e:
        flag = -1
        add_mysql_check(host_ip, "Threads_running", "exception", "chk_mysql_threads_connected out exception")

#不能立即或者表锁的次数
def chk_mysql_table_locks_waited(host_ip,host_port,host_user,host_pwd):
    host = (host_ip, str(func.mysql_bin)+'mysql -u' + host_user + ' -p' + host_pwd + ' -P' + str(host_port) + ' -h' + host_ip + ' -e "show status like \'Table_locks_waited\'"')
    items = [('Table_locks_waited')]
    flag=0
    try:
        p = os.popen(host[1])
        for line in p.readlines():
             line=line.decode('cp936').encode('utf-8')
             for item in items:
                 if line.find(item[0]) > -1:
                     add_mysql_check(host_ip, "Table_locks_waited", "normal",
                                     line.replace('\t', '').replace('Table_locks_waited', '').replace("\n", ""))
                     flag=1
        if flag==0:
            add_mysql_check(host_ip, "Table_locks_waited", "error","Table_locks_waited is unreachable")
    except Exception, e:
        flag = -1
        add_mysql_check(host_ip, "Table_locks_waited", "exception", "Table_locks_waited out exception")
#立即获得的表的锁的次数
def chk_mysql_table_locks_immediate(host_ip,host_port,host_user,host_pwd):
    host = (host_ip, str(func.mysql_bin)+'mysql -u' + host_user + ' -p' + host_pwd + ' -P' + str(
        host_port) + ' -h' + host_ip + ' -e "show status like \'Table_locks_immediate\'"')
    items = [('Table_locks_immediate')]
    flag=0
    try:
        p = os.popen(host[1])
        for line in p.readlines():
             line=line.decode('cp936').encode('utf-8')
             for item in items:
                 if line.find(item[0]) > -1:
                   flag=1
                   add_mysql_check(host_ip, "Table_locks_immediate", "normal",
                                 line.replace('\t', '').replace('Table_locks_immediate', '').replace("\n", ""))
        if flag == 0:
                 add_mysql_check(host_ip, "Table_locks_immediate", "error", "Table_locks_immediate is unreachable")
    except Exception, e:
        flag = -1
        add_mysql_check(host_ip, "Table_locks_immediate", "exception", "Table_locks_immediate out exception")
#The number of fsync() operations so far.
def chk_mysql_innodb_data_fsyncs(host_ip,host_port,host_user,host_pwd):
    host = (host_ip, str(func.mysql_bin)+'mysql -u' + host_user + ' -p' + host_pwd + ' -P' + str(
        host_port) + ' -h' + host_ip + ' -e "show status like \'Innodb_data_fsyncs\'"')
    items = [('Innodb_data_fsyncs')]
    flag=0
    try:
        p = os.popen(host[1])
        for line in p.readlines():
             line=line.decode('cp936').encode('utf-8')
             for item in items:
                 if line.find(item[0]) > -1:
                     add_mysql_check(host_ip, "Innodb_data_fsyncs", "normal",
                                     line.replace('\t', '').replace('Innodb_data_fsyncs', '').replace("\n", ""))
                     flag=1
        if flag == 0:
            add_mysql_check(host_ip, "Innodb_data_fsyncs", "error", "Innodb_data_fsyncs is unreachable")
    except Exception, e:
        flag = -1
        add_mysql_check(host_ip, "Innodb_data_fsyncs", "exception", "Innodb_data_fsyncs out exception")

#Innodb_data_pending_fsyncs
def chk_mysql_innodb_data_pending_fsyncs(host_ip,host_port,host_user,host_pwd):
    host = (host_ip, str(func.mysql_bin)+'mysql -u' + host_user + ' -p' + host_pwd + ' -P' + str(
        host_port) + ' -h' + host_ip + ' -e "show status like \'Innodb_data_pending_fsyncs\'"')
    items = [('Innodb_data_pending_fsyncs')]
    flag=0
    try:
        p = os.popen(host[1])
        for line in p.readlines():
             line=line.decode('cp936').encode('utf-8')
             for item in items:
                 if line.find(item[0]) > -1:
                     add_mysql_check(host_ip, "Innodb_data_pending_fsyncs", "normal",
                                     line.replace('\t', '').replace('Innodb_data_pending_fsyncs', '').replace("\n", ""))
                     flag=1
        if flag == 0:
            add_mysql_check(host_ip, "Innodb_data_pending_fsyncs", "error", "Innodb_data_pending_fsyncs is unreachable")
    except Exception, e:
        flag = -1
        add_mysql_check(host_ip, "Innodb_data_pending_fsyncs", "exception", "Innodb_data_pending_fsyncs out exception")
#chk_mysql_innodb_data_pending_reads
def chk_mysql_innodb_data_pending_reads(host_ip,host_port,host_user,host_pwd):
    host = (host_ip, str(func.mysql_bin)+'mysql -u' + host_user + ' -p' + host_pwd + ' -P' + str(
        host_port) + ' -h' + host_ip + ' -e "show status like \'Innodb_data_pending_reads\'"')
    items = [('Innodb_data_pending_reads')]
    flag = 0
    try:
        p = os.popen(host[1])
        for line in p.readlines():
             line=line.decode('cp936').encode('utf-8')
             for item in items:
                 if line.find(item[0]) > -1:
                     add_mysql_check(host_ip, "Innodb_data_pending_reads", "normal",
                                     line.replace('\t', '').replace('Innodb_data_pending_reads', '').replace("\n", ""))
                     flag = 1
        if flag == 0:
            add_mysql_check(host_ip, "Innodb_data_pending_reads", "error", "Innodb_data_pending_reads is unreachable")
    except Exception, e:
        flag = -1
        add_mysql_check(host_ip, "Innodb_data_pending_reads", "exception", "Innodb_data_pending_reads out exception")

#chk_mysql_innodb_data_pending_writes
def chk_mysql_innodb_data_pending_writes(host_ip,host_port,host_user,host_pwd):
    host = (host_ip, str(func.mysql_bin)+'mysql -u' + host_user + ' -p' + host_pwd + ' -P' + str(
        host_port) + ' -h' + host_ip + ' -e "show status like \'Innodb_data_pending_writes\'"')
    items = [('Innodb_data_pending_writes')]
    flag = 0
    try:
        p = os.popen(host[1])
        for line in p.readlines():
             line=line.decode('cp936').encode('utf-8')
             for item in items:
                 if line.find(item[0]) > -1:
                    flag = 1
                    add_mysql_check(host_ip, "Innodb_data_pending_writes", "normal",
                                 line.replace('\t', '').replace('Innodb_data_pending_writes', '').replace("\n", ""))
        if flag == 0:
            add_mysql_check(host_ip, "Innodb_data_pending_writes", "error", "Innodb_data_pending_writes is unreachable")
    except Exception, e:
        flag = -1
        add_mysql_check(host_ip, "Innodb_data_pending_writes", "exception", "Innodb_data_pending_writes out exception")
#chk_mysql_innodb_log_write_requests
def chk_mysql_innodb_log_write_requests(host_ip,host_port,host_user,host_pwd):
    host = (host_ip, str(func.mysql_bin)+'mysql -u' + host_user + ' -p' + host_pwd + ' -P' + str(
        host_port) + ' -h' + host_ip + ' -e "show status like \'Innodb_log_write_requests\'"')
    items = [('Innodb_log_write_requests')]
    flag=0
    try:
        p = os.popen(host[1])
        for line in p.readlines():
             line=line.decode('cp936').encode('utf-8')
             for item in items:
                 if line.find(item[0]) > -1:
                    flag=1
                    add_mysql_check(host_ip, "Innodb_log_write_requests", "normal",
                                    line.replace('\t', '').replace('Innodb_log_write_requests', '').replace("\n", ""))
        if flag == 0:
            add_mysql_check(host_ip, "Innodb_log_write_requests", "error", "Innodb_log_write_requests is unreachable")
    except Exception, e:
            add_mysql_check(host_ip, "Innodb_log_write_requests", "exception", "Innodb_log_write_requests  out exception")


#chk_mysql_innodb_log_writes
def chk_mysql_innodb_log_writes(host_ip,host_port,host_user,host_pwd):
    host = (host_ip, str(func.mysql_bin)+'mysql -u' + host_user + ' -p' + host_pwd + ' -P' + str(
        host_port) + ' -h' + host_ip + ' -e "show status like \'Innodb_log_writes\'"')
    items = [('Innodb_log_writes')]
    flag = 0
    try:
        p = os.popen(host[1])
        for line in p.readlines():
             line=line.decode('cp936').encode('utf-8')
             for item in items:
                 if line.find(item[0]) > -1:
                     flag = 1
                     add_mysql_check(host_ip, "Innodb_log_writes", "normal",
                       line.replace('\t', '').replace('Innodb_log_writes', '').replace("\n", ""))
        if flag == 0:
            add_mysql_check(host_ip, "Innodb_log_writes", "error", "Innodb_log_writes is unreachable")
    except Exception, e:
        add_mysql_check(host_ip, "Innodb_log_writes", "exception", "Innodb_log_writes  out exception")

#chk_mysql_innodb_buffer_hit_radio
def chk_mysql_Innodb_buffer_pool_reads(host_ip,host_port,host_user,host_pwd):
    host = (host_ip, str(func.mysql_bin)+'mysql -u' + host_user + ' -p' + host_pwd + ' -P' + str(
        host_port) + ' -h' + host_ip + ' -e "show status like \'Innodb_buffer_pool_reads\'"')
    items = [('Innodb_buffer_pool_reads')]
    flag = 0
    try:
        p = os.popen(host[1])
        for line in p.readlines():
             line=line.decode('cp936').encode('utf-8')
             for item in items:
                 if line.find(item[0]) > -1:
                     flag = 1
                     add_mysql_check(host_ip, "Innodb_buffer_pool_reads", "normal",
                       line.replace('\t', '').replace('Innodb_buffer_pool_reads', '').replace("\n", ""))
        if flag == 0:
            add_mysql_check(host_ip, "Innodb_buffer_pool_reads", "error", "Innodb_buffer_pool_reads is unreachable")
    except Exception, e:
        add_mysql_check(host_ip, "Innodb_buffer_pool_reads", "exception", "Innodb_buffer_pool_reads  out exception")

#chk_mysql_Innodb_buffer_pool_read_requests
def chk_mysql_Innodb_buffer_pool_read_requests(host_ip, host_port, host_user, host_pwd):
    host = (host_ip, str(func.mysql_bin)+'mysql -u' + host_user + ' -p' + host_pwd + ' -P' + str(
        host_port) + ' -h' + host_ip + ' -e "show status like \'Innodb_buffer_pool_read_requests\'"')
    items = [('Innodb_buffer_pool_read_requests')]
    flag = 0
    try:
        p = os.popen(host[1])
        for line in p.readlines():
            line = line.decode('cp936').encode('utf-8')
            for item in items:
                if line.find(item[0]) > -1:
                    flag = 1
                    add_mysql_check(host_ip, "Innodb_buffer_pool_read_requests", "normal",
                                    line.replace('\t', '').replace('Innodb_buffer_pool_read_requests', '').replace("\n", ""))
        if flag == 0:
            add_mysql_check(host_ip, "Innodb_buffer_pool_read_requests", "error", "Innodb_buffer_pool_read_requests is unreachable")
    except Exception, e:
        add_mysql_check(host_ip, "Innodb_buffer_pool_read_requests", "exception", "Innodb_buffer_pool_read_requests  out exception")

#chk_mysql_Qcache_hits
def chk_mysql_Qcache_hits(host_ip, host_port, host_user, host_pwd):
    host = (host_ip, str(func.mysql_bin)+'mysql -u' + host_user + ' -p' + host_pwd + ' -P' + str(
        host_port) + ' -h' + host_ip + ' -e "show status like \'Qcache_hits\'"')
    items = [('Qcache_hits')]
    flag = 0
    try:
        p = os.popen(host[1])
        for line in p.readlines():
            line = line.decode('cp936').encode('utf-8')
            for item in items:
                if line.find(item[0]) > -1:
                    flag = 1
                    add_mysql_check(host_ip, "Qcache_hits", "normal",
                                    line.replace('\t', '').replace('Qcache_hits', '').replace("\n", ""))
        if flag == 0:
            add_mysql_check(host_ip, "Qcache_hits", "error", "Qcache_hits is unreachable")
    except Exception, e:
        add_mysql_check(host_ip, "Qcache_hits", "exception", "Qcache_hits  out exception")

#chk_mysql_Qcache_hits
def chk_mysql_Qcache_inserts(host_ip, host_port, host_user, host_pwd):
    host = (host_ip, str(func.mysql_bin)+'mysql -u' + host_user + ' -p' + host_pwd + ' -P' + str(
        host_port) + ' -h' + host_ip + ' -e "show status like \'Qcache_inserts\'"')
    items = [('Qcache_inserts')]
    flag = 0
    try:
        p = os.popen(host[1])
        for line in p.readlines():
            line = line.decode('cp936').encode('utf-8')
            for item in items:
                if line.find(item[0]) > -1:
                    flag = 1
                    add_mysql_check(host_ip, "Qcache_inserts", "normal",
                                    line.replace('\t', '').replace('Qcache_inserts', '').replace("\n", ""))
        if flag == 0:
            add_mysql_check(host_ip, "Qcache_inserts", "error", "Qcache_inserts is unreachable")
    except Exception, e:
        add_mysql_check(host_ip, "Qcache_inserts", "exception", "Qcache_inserts  out exception")

#chk_mysql_Qcache_hits
def chk_mysql_Threads_created(host_ip, host_port, host_user, host_pwd):
    host = (host_ip, str(func.mysql_bin)+'mysql -u' + host_user + ' -p' + host_pwd + ' -P' + str(
        host_port) + ' -h' + host_ip + ' -e "show status like \'Threads_created\'"')
    items = [('Threads_created')]
    flag = 0
    try:
        p = os.popen(host[1])
        for line in p.readlines():
            line = line.decode('cp936').encode('utf-8')
            for item in items:
                if line.find(item[0]) > -1:
                    flag = 1
                    add_mysql_check(host_ip, "Threads_created", "normal",
                                    line.replace('\t', '').replace('Threads_created', '').replace("\n", ""))
        if flag == 0:
            add_mysql_check(host_ip, "Threads_created", "error", "Threads_created is unreachable")
    except Exception, e:
        add_mysql_check(host_ip, "Threads_created", "exception", "Threads_created  out exception")

#chk_mysql_Connections
def chk_mysql_Connections(host_ip, host_port, host_user, host_pwd):
    host = (host_ip, str(func.mysql_bin)+'mysql -u' + host_user + ' -p' + host_pwd + ' -P' + str(
        host_port) + ' -h' + host_ip + ' -e "show status like \'Connections\'"')
    items = [('Connections')]
    flag = 0
    try:
        p = os.popen(host[1])
        for line in p.readlines():
            line = line.decode('cp936').encode('utf-8')
            for item in items:
                if line.find(item[0]) > -1:
                    flag = 1
                    add_mysql_check(host_ip, "Connections", "normal",
                                    line.replace('\t', '').replace('Connections', '').replace("\n", ""))
        if flag == 0:
            add_mysql_check(host_ip, "Connections", "error", "Connections is unreachable")
    except Exception, e:
        add_mysql_check(host_ip, "Connections", "exception", "Connections  out exception")
#chk_mysql_Com_commit
def chk_mysql_Com_commit(host_ip, host_port, host_user, host_pwd):
    host = (host_ip, str(func.mysql_bin)+'mysql -u' + host_user + ' -p' + host_pwd + ' -P' + str(
        host_port) + ' -h' + host_ip + ' -e "show  global status like \'Com_commit\'"')
    items = [('Com_commit')]
    flag = 0
    try:
        p = os.popen(host[1])
        for line in p.readlines():
            line = line.decode('cp936').encode('utf-8')
            for item in items:
                if line.find(item[0]) > -1:
                    flag = 1
                    add_mysql_check(host_ip, "Com_commit", "normal",
                                    line.replace('\t', '').replace('Com_commit', '').replace("\n", ""))
        if flag == 0:
            add_mysql_check(host_ip, "Com_commit", "error", "Com_commit is unreachable")
    except Exception, e:
        add_mysql_check(host_ip, "Com_commit", "exception", "Com_commit  out exception")
#chk_mysql_Com_rollback
def chk_mysql_Com_rollback(host_ip, host_port, host_user, host_pwd):
    host = (host_ip, str(func.mysql_bin)+'mysql -u' + host_user + ' -p' + host_pwd + ' -P' + str(
        host_port) + ' -h' + host_ip + ' -e "show global status like \'Com_rollback\'"')
    items = [('Com_rollback')]
    flag = 0
    try:
        p = os.popen(host[1])
        for line in p.readlines():
            line = line.decode('cp936').encode('utf-8')
            for item in items:
                if line.find(item[0]) > -1:
                    flag = 1
                    add_mysql_check(host_ip, "Com_rollback", "normal",
                                    line.replace('\t', '').replace('Com_rollback', '').replace("\n", ""))
        if flag == 0:
            add_mysql_check(host_ip, "Com_rollback", "error", "Com_rollback is unreachable")
    except Exception, e:
        add_mysql_check(host_ip, "Com_rollback", "exception", "Com_rollback  out exception")

#chk_mysql_Com_rollback
def chk_mysql_Questions(host_ip, host_port, host_user, host_pwd):
    host = (host_ip, str(func.mysql_bin)+'mysql -u' + host_user + ' -p' + host_pwd + ' -P' + str(
        host_port) + ' -h' + host_ip + ' -e "show  global status like \'Questions\'"')
    items = [('Questions')]
    flag = 0
    try:
        p = os.popen(host[1])
        for line in p.readlines():
            line = line.decode('cp936').encode('utf-8')
            for item in items:
                if line.find(item[0]) > -1:
                    flag = 1
                    add_mysql_check(host_ip, "Questions", "normal",
                                    line.replace('\t', '').replace('Questions', '').replace("\n", "").replace("\r", ""))
        if flag == 0:
            add_mysql_check(host_ip, "Questions", "error", "Questions is unreachable")
    except Exception, e:
        add_mysql_check(host_ip, "Questions", "exception", "Questions  out exception")

def get_mysql_processinfo(host_ip):
    try:
        datalist,columns=mysql_func.get_query_by_ipaddr(host_ip,"select a.COMMAND,a.STATE,count(1)  from information_schema.`PROCESSLIST` a where a.COMMAND not in (\'Sleep\') group by a.COMMAND,a.STATE having count(1)>5")
        for i in datalist:
            add_mysql_check_command(host_ip, i[0], i[1], i[2])
    except Exception, e:
        add_mysql_check(host_ip, "get_mysql_processinfo", "exception", "get_mysql_processinfo  out exception")


def chk_mysql(host_ip,host_port,host_user,host_pwd):
    chk_mysqlping(host_ip, host_port, host_user, host_pwd)
    chk_mysql_threads_connected(host_ip, host_port, host_user, host_pwd)
    chk_mysql_threads_running(host_ip, host_port, host_user, host_pwd)
    chk_mysql_table_locks_waited(host_ip, host_port, host_user, host_pwd)
    chk_mysql_table_locks_immediate(host_ip, host_port, host_user, host_pwd)
    chk_mysql_innodb_data_fsyncs(host_ip, host_port, host_user, host_pwd)
    chk_mysql_innodb_data_pending_fsyncs(host_ip, host_port, host_user, host_pwd)
    chk_mysql_innodb_data_pending_reads(host_ip, host_port, host_user, host_pwd)
    chk_mysql_innodb_data_pending_writes(host_ip, host_port, host_user, host_pwd)
    chk_mysql_innodb_log_write_requests(host_ip, host_port, host_user, host_pwd)
    chk_mysql_innodb_log_writes(host_ip, host_port, host_user, host_pwd)
    chk_mysql_Innodb_buffer_pool_reads(host_ip, host_port, host_user, host_pwd)
    chk_mysql_Innodb_buffer_pool_read_requests(host_ip, host_port, host_user, host_pwd)
    chk_mysql_Qcache_hits(host_ip, host_port, host_user, host_pwd)
    chk_mysql_Qcache_inserts(host_ip, host_port, host_user, host_pwd)
    chk_mysql_Threads_created(host_ip, host_port, host_user, host_pwd)
    chk_mysql_Connections(host_ip, host_port, host_user, host_pwd)
    chk_mysql_Com_commit(host_ip, host_port, host_user, host_pwd)
    chk_mysql_Com_rollback(host_ip, host_port, host_user, host_pwd)
    chk_mysql_Questions(host_ip, host_port, host_user, host_pwd)
    get_mysql_processinfo(host_ip)

def monitor():
    threads = []
    list_hosts=func.get_mysql_hosts_list_run("using")
    # mythread =threading.Thread(target=loop,args=(skey,intval_time,next_time,sqlstr,spatch,sfilename,mail_list,str_title,str_content))
    pc = prpcrypt()
    for host in list_hosts:
        host_ip=host.hosts_ip
        host_port=host.host_port
        host_user=host.host_user
        host_pwd=pc.decrypt(host.host_pwd)
        mythread = threading.Thread(target=chk_mysql ,args=(host_ip,host_port,host_user,host_pwd))
        threads.append(mythread)
    for t in threads:
            t.setDaemon(True)
            t.start()
        #等待所有结束线程
    for s in threads:
            s.join()


def get_mysql_spaceinfo(host_ip):
    try:
        datalist,columns=mysql_func.get_query_by_ipaddr(host_ip,"select a.`TABLE_SCHEMA`,a.`TABLE_NAME`,a.`TABLE_ROWS`,a.`DATA_LENGTH` from information_schema.`TABLES` a where a.`TABLE_SCHEMA` not in ('information_schema','mysql','test','performance_schema')")
        for i in datalist:
            add_mysql_check_space(host_ip, i[0], i[1], i[2], i[3])
    except Exception, e:
        print(e.message)
        add_mysql_check(host_ip, "get_mysql_spaceinfo", "exception", "get_mysql_spaceinfo  out exception")

def chk_mysql_h(host_ip,host_port,host_user,host_pwd):
    get_mysql_spaceinfo(host_ip)
def monitor_h():
    threads = []
    list_hosts=func.get_mysql_hosts_list_run("using")
    # mythread =threading.Thread(target=loop,args=(skey,intval_time,next_time,sqlstr,spatch,sfilename,mail_list,str_title,str_content))
    pc = prpcrypt()
    for host in list_hosts:
        host_ip=host.hosts_ip
        host_port=host.host_port
        host_user=host.host_user
        host_pwd=pc.decrypt(host.host_pwd)
        mythread = threading.Thread(target=chk_mysql_h ,args=(host_ip,host_port,host_user,host_pwd))
        threads.append(mythread)
    for t in threads:
            t.setDaemon(True)
            t.start()
        #等待所有结束线程
    for s in threads:
            s.join()