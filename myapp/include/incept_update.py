#!/usr/bin/python
#_*_coding:utf-8 _*_
import MySQLdb
inception_host={
    "incp_host":"192.168.188.211",
    "incp_user":"root",
    "incp_passwd":"123321",
    "incp_port":6669
}
mysql_host={
    "mysql_ip": "192.168.188.111",
    "mysql_port": 3306,
    "mysql_user": "test",
    "mysql_passwd": "test",
}
def update_sql_chk(sql):
    incp_host=inception_host['incp_host']
    incp_user = inception_host['incp_user']
    incp_passwd = inception_host['incp_passwd']
    incp_port = inception_host['incp_port']
    mysql_ip=mysql_host['mysql_ip']
    mysql_port=mysql_host['mysql_port']
    mysql_user=mysql_host['mysql_user']
    mysql_passwd=mysql_host['mysql_passwd']
    try:
        sql1="/*--user=%s;--password=%s;--host=%s;%s;--port=%d;*/\
            inception_magic_start;"%(mysql_user,mysql_passwd,mysql_ip,"--enable-check",mysql_port)
        sql2='inception_magic_commit;'
        sql = sql1 + sql + sql2
        conn = MySQLdb.connect(host=incp_host, user=incp_user, passwd=incp_passwd, db='', port=incp_port, use_unicode=True,
                               charset="utf8")
        cur = conn.cursor()
        ret = cur.execute(sql)
        result = cur.fetchall()
        # num_fields = len(cur.description)
        field_names = [i[0] for i in cur.description]
        cur.close()
        conn.close()
    except MySQLdb.Error, e:
        return ([str(e)], ''), ['error']
    return result, field_names

def readFile(filename):
    fopen = open(filename, 'r')
    append_str=""
    for eachLine in fopen:
        if len(eachLine.strip())==0:
            pass
        elif eachLine.strip().lower().find("#") == 0:
            pass
        elif eachLine.strip().lower().find("--") == 0:
            pass
        else:
            append_str=append_str+"\r\n"+eachLine;
    return append_str
    fopen.close()
if __name__ == '__main__':
    source = "/opt/dev/scripts/meta_data.sql"
    sql_str=readFile(source)
    if len(sql_str)>0:
        update_sql_chk(sql_str)