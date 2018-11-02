#!/usr/bin/python
#_*_coding:utf-8 _*_
import MySQLdb
from myapp.include.encrypt import prpcrypt
from myapp.models import mysql_hosts
from django.db import connection, connections
def make_sure_mysql_usable():
    # mysql is lazily connected to in django.
    # connection.connection is None means
    # you have not connected to mysql before
    if connection.connection and not connection.is_usable():
        # destroy the default mysql connection
        # after this line, when you use ORM methods
        # django will reconnect to the default mysql
        del connections._connections.default

def get_mysqlhost(ipaddr):
    make_sure_mysql_usable()
    host = mysql_hosts.objects.get(hosts_ip=ipaddr)
    return host

def get_query_by_ipaddr(ipaddr,sql):
    try:
        host = get_mysqlhost(ipaddr)
        pc = prpcrypt()
        passwd=pc.decrypt(host.host_pwd)
        conn=MySQLdb.connect(host=host.hosts_ip,user=host.host_user,passwd=passwd,port=int(host.host_port),connect_timeout=5,charset='utf8')
        cursor = conn.cursor()
        count=cursor.execute(sql)
        index=cursor.description
        col=[]
        #get column name
        for i in index:
            col.append(i[0])
        #result=cursor.fetchall()
        result=cursor.fetchall()
        cursor.close()
        conn.close()
        return (result,col)
    except Exception,e:
        return([str(e)],''),['error']