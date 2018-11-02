#!/usr/bin/python
#_*_coding:utf-8 _*_
import os
import datetime
from optparse import OptionParser
import urllib,urllib2
import json
import sys
import simplejson
import os
reload(sys)
sys.setdefaultencoding('utf-8')
'''https://work.weixin.qq.com/wework_admin/frame#contacts'''
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
def get_user_paras():
    try:
        opt = OptionParser()
        opt.add_option('--host_ip',
                       dest='host_ip',
                       type=str,
                       help='the ip of the check mysql host')
        opt.add_option('--host_port',
                       dest='host_port',
                       type=int,
                       help='the host_port of the check mysql ')
        opt.add_option('--host_user',
                       dest='host_user',
                       type=str,
                       help='the host_user of the check mysql ')
        opt.add_option('--host_pwd',
                       dest='host_pwd',
                       type=str,
                       help='the host_pwd of the check mysql ')
        opt.add_option('--check_type',
                       dest='check_type',
                       type=str,
                       help='the check_type of the check mysql ')
        opt.add_option('--run',
                       action="store_true",
                       dest="is_run",
                       default=False,
                       help="run the scripts")
        opt.add_option('--view',
                       action="store_false",
                       dest="is_run",
                       default=False,
                       help="only view but not run the scripts")
        opt.add_option('--show_type',
                       dest="show_type",
                       type=int,
                       default=0,
                       help="0 or 1, 0 only show the simple data, 1 show the full data")
        (options, args) = opt.parse_args()
        is_valid_paras = True
        error_messages = []
        host_ip = options.host_ip
        host_port = options.host_port
        host_user = options.host_user
        host_pwd = options.host_pwd
        check_type = options.check_type
        is_run = options.is_run
        show_type = options.show_type
        if not host_ip:
            error_messages.append("host_ip must be set;")
            is_valid_paras = False
        if not host_port:
            error_messages.append("host_port must be set;")
            is_valid_paras = False
        if not host_user:
            error_messages.append("host_user must be set;")
            is_valid_paras = False
        if not host_pwd:
            error_messages.append("host_pwd must be set;")
            is_valid_paras = False
        if check_type not in ["mysql_alive", "mysql_uptime", "mysql_threads_connected", "mysql_threads_running","mysql_locks_waited", "mysql_locks_immediate", "mysql_data_fsyncs", "mysql_data_pending_fsyncs",
            "mysql_data_pending_reads", "mysql_data_pending_writes", "mysql_log_write_requests", "mysql_log_writes",
            "mysql_innodb_buffer_pool_read", "mysql_qps", "mysql_tps"
        ]:

            error_messages.append("check_type must be set;")
            is_valid_paras = False
        if show_type not in [0, 1]:
            error_messages.append("show_type only can be 0 or 1;")
            is_valid_paras = False

        if is_valid_paras:
            user_paras = {"host_ip": host_ip, "host_port":host_port,"host_user":host_user,"host_pwd":host_pwd,"check_type":check_type,"is_run": is_run, "show_type": show_type}
            return user_paras
        else:
            for error_message in error_messages:
                print(error_message)
                opt.print_help()
            return None
    except Exception as ex:
        print("exception :{0}".format(str(ex)))
        return None

def chk_mysqlping(host_ip,host_port,host_user,host_pwd):
    host = (host_ip,'mysqladmin -u'+host_user+' -p'+host_pwd+' -P'+str(host_port)+'  -h'+host_ip+' ping')
    items = [('mysqld','is alive')]
    flag = 0;
    try:
        p = os.popen(host[1])
        for line in p.readlines():
             for item in items:
                 if line.find(item[0]) > -1:
                     if line.find(item[1]) > -1:
                       flag=1;
                       #success
        if flag == 0:
            # error
            wxsenddata('YueRenLiang', '【' + host[0] + '】', '[mysqld is unreachable]')
    except Exception, e:
            flag=-1
            wxsenddata('YueRenLiang', 'MYSQL chk_mysqlping', '[TIME]:' + str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) + '\r\n' + '[TYPE]:high' + '\r\n'
                     + '[IP]' + host[0] + '\r\n' + '[MSG]:chk_mysqlping not  available')
    finally:
            return flag
def monitor():
    user_paras = get_user_paras()
    if user_paras is None:
        sys.exit(-99)
    info = "host_ip:{0},host_port:{1},host_user:{2},host_pwd:{3},check_type:{4}"
    info = info.format(user_paras["host_ip"],
                       user_paras["host_port"],
                       user_paras["host_user"],
                       user_paras["host_pwd"],
                       user_paras["check_type"])
    print(user_paras["check_type"])
    if user_paras["check_type"]=="mysql_alive":
        result=chk_mysqlping(user_paras["host_ip"],user_paras["host_port"],user_paras["host_user"], user_paras["host_pwd"])
    elif user_paras["check_type"]=="mysql_uptime":
        chk_mysqlping()
    else:
        print "check_type must be set;"