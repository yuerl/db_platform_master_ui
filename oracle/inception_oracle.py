# -*- coding: utf-8 -*-
import sys,uuid
reload(sys)
sys.setdefaultencoding('utf-8')
from myapp.include import function as func,sqlfilter
import MySQLdb,sys,string,time,datetime,uuid,pymongo,json,cx_Oracle,os
from django.contrib.auth.models import User
from myapp.models import Db_name,Db_account,Db_instance
from myapp.etc import config
from django.core.serializers.json import DjangoJSONEncoder
from myapp.models import Oper_log
from myapp.include.encrypt import prpcrypt
import oracle_fun
select_limit = int(config.select_limit)
export_limit = int(config.export_limit)
wrong_msg = config.wrong_msg
public_user = config.public_user
os.environ['NLS_LANG'] = 'AMERICAN_AMERICA.AL32UTF8'

incept_backup_host = config.incept_backup_host
incept_backup_port = config.incept_backup_port
incept_backup_user = config.incept_backup_user
incept_backup_passwd = config.incept_backup_passwd

#判断备份的数据库是否存在，如果不存在就创建，存在就不创建
def backupdb_check_db(user,passwd,host,port,dbname):
	str_db=str(host).replace('.','_')+'_'+str(port)+'_'+str(user).lower()
	chk_sql="SELECT count(1) rowcount FROM mysql.`db` a WHERE a.db='%s'"%str_db
	results_0, col_0=func.mysql_query(chk_sql, incept_backup_user, incept_backup_passwd, incept_backup_host,
	                 int(incept_backup_port), 'mysql')
	if results_0 is not None:
		if long(str(results_0[0][0]))<1:
			cdb_sql="CREATE DATABASE IF NOT EXISTS %s default charset utf8 COLLATE utf8_general_ci"%str_db
			rowsinfo, sucess_flag =func.mysql_exec(cdb_sql, incept_backup_user, incept_backup_passwd, incept_backup_host, int(incept_backup_port),'mysql')
	str_inception_backup_information='$_$inception_backup_information$_$'
	chk_sql_inception_backup_information = "select count(1) rowcount from information_schema.`TABLES` a where a.TABLE_SCHEMA='%s' and a.TABLE_NAME='%s'"%(str_db,str_inception_backup_information)
	results_1, col_1 = func.mysql_query(chk_sql_inception_backup_information, incept_backup_user, incept_backup_passwd, incept_backup_host,
	                                int(incept_backup_port), 'mysql')
	if results_1 is not None:
		if long(str(results_1[0][0]))<1:
			str_inception_backup_information_ddl='''CREATE TABLE `$_$inception_backup_information$_$` (
		  `opid_time` varchar(50) NOT NULL DEFAULT '',
		  `start_binlog_file` varchar(512) DEFAULT NULL,
		  `start_binlog_pos` int(11) DEFAULT NULL,
		  `end_binlog_file` varchar(512) DEFAULT NULL,
		  `end_binlog_pos` int(11) DEFAULT NULL,
		  `sql_statement` text,
		  `host` varchar(64) DEFAULT NULL,
		  `dbname` varchar(64) DEFAULT NULL,
		  `tablename` varchar(64) DEFAULT NULL,
		  `port` int(11) DEFAULT NULL,
		  `time` timestamp NULL DEFAULT NULL,
		  `type` varchar(20) DEFAULT NULL,
		  PRIMARY KEY (`opid_time`)
		) ENGINE=InnoDB DEFAULT CHARSET=utf8'''
			results_2, col_2 = func.mysql_exec(str_inception_backup_information_ddl, incept_backup_user, incept_backup_passwd, incept_backup_host,
	                                int(incept_backup_port),str_db)
#判断表是否存在
def backupdb_check_table(user,passwd,host,port,dbname,tablename,undo_sql,sequence,sql,in_sql_type):
	str_db=str(host).replace('.','_')+'_'+str(port)+'_'+str(user).lower()
	chk_sql_inception_backup_information = "select count(1) rowcount from information_schema.`TABLES` a where a.TABLE_SCHEMA='%s' and a.TABLE_NAME='%s'"%(str_db,tablename)
	results_1, col_1 = func.mysql_query(chk_sql_inception_backup_information, incept_backup_user, incept_backup_passwd, incept_backup_host,
	                                int(incept_backup_port), str_db)
	if results_1 is not None:
		if long(str(results_1[0][0]))<1:
			str_inception_backup_table='''CREATE TABLE %s (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `rollback_statement` mediumtext,
  `opid_time` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8'''% tablename
			results_2, col_2 = func.mysql_exec(str_inception_backup_table, incept_backup_user, incept_backup_passwd, incept_backup_host,
	                                int(incept_backup_port),str_db)
	#insert into inception_backup_information
	sql_inception_backup_information='''INSERT INTO %s.`$_$inception_backup_information$_$` (`opid_time`, `start_binlog_file`, `start_binlog_pos`, `end_binlog_file`, `end_binlog_pos`, `sql_statement`, `host`, `dbname`, `tablename`, `port`, `time`, `type`) VALUES 
	('%s', '', '0', '', '0', "%s", '%s', '%s', '%s', '%s',now(), '%s')'''%(str_db,sequence,sql,host,dbname,tablename,str(port),str(in_sql_type).upper())
	rowcount0,info0=func.mysql_exec(sql_inception_backup_information, incept_backup_user, incept_backup_passwd, incept_backup_host, int(incept_backup_port),
	                str_db)
	#insert into tble
	sql_inception_backup_table='''INSERT INTO %s.%s ( `rollback_statement`, `opid_time`) VALUES
 	( "%s", '%s')'''%(str_db,tablename,undo_sql,sequence)
	rowcount1, info1 =func.mysql_exec(sql_inception_backup_table, incept_backup_user, incept_backup_passwd, incept_backup_host, int(incept_backup_port),
	                str_db)
	if info0[0]=='success' and info1[0]=='success':
		return 'success',1
	else:
		return 'failed',0


#根据；被拆分的sql如果是dml进行备份。
def backupdml_insert(single_sql,user,passwd,host,port,dbname):
	single_sql=single_sql.replace('\r','').replace('\n','')
	sqltype=sqlfilter.get_sqltype(single_sql)
	list_sql_return=[]
	str_sql_where = 'where 1=1'
	sql_table='error'
	if sqltype=='insert':
		temp_list=str(single_sql).lower().strip().replace('(',' ( ').replace(')',' ) ').split(' ')
		sql_table=str(temp_list[2])
		list_items=str(single_sql).lower().strip().replace(' ','').replace('insertinto'+sql_table+'(','(').split(')values(')
		if len(list_items)==2:
			str_cols=str(list_items[0])[1:]
			str_value=str(list_items[1])[:len(list_items[1])-1]
			list_str_cols=str_cols.split(',')
			list_str_value=str_value.split(',')
			for i in range(len(list_str_cols)):
				str_sql_where=str_sql_where+' and '+list_str_cols[i]+'='+list_str_value[i]

		str_sql_where='delete from '+sql_table+' '+str_sql_where+';'
		list_sql_return.append(str_sql_where)
	elif sqltype=='update':
		str_set_pos=str(single_sql).find('set')
		str_where_pos = str(single_sql).find('where')
		list_temp=str(single_sql).strip().lower().split(" ")
		if len(list_temp)>2:
			sql_table=list_temp[1]
		sql_where=str(single_sql)[long(str_where_pos):]
		sql_set_left=str(single_sql)[:long(str_set_pos)]
		sql_set_right=str(single_sql)[long(str_set_pos)+3:long(str_where_pos)]
		list_colums=sql_set_right.lower().strip().split(',')
		sql_undo_select='select rowid,'
		for i in range(len(list_colums)):
			sql_undo_select=sql_undo_select+' '+list_colums[i].split('=')[0]+','
		sql_undo_select=str(sql_undo_select)[:len(sql_undo_select)-1]
		sql_undo_select=sql_undo_select+" from "+sql_set_left.lower().replace('update','').strip()+' '+sql_where
		result, col=oracle_fun.oracle_query(sql_undo_select,user,passwd,host,port,dbname)
		for m in range(len(result)):
			#sql_undo='update '+sql_table+' set '+ col[1]+'='+result[m][1]+','+col[2]+'='+result[m][2]+' where rowid='+result[m][0]
			temp_set=""
			for p in range(len(col)-1):
				temp_set=temp_set+col[p+1]+'='+result[m][p+1]+','
			temp_set=temp_set[:len(temp_set)-1]
			sql_undo = 'update ' + sql_table +' set '+ temp_set + ' where rowid=' + result[m][0]+';'
			list_sql_return.append(sql_undo)
	elif sqltype == 'delete':
		list_temp=single_sql.lower().strip().split(' ')
		sql_table=list_temp[2]
		str_where_pos = str(single_sql).lower().find('where')
		str_from_pos  =str(single_sql).lower().find('from')
		sql_undo_select='select *  '+str(str(single_sql).lower())[str_from_pos:str_where_pos]+ str(single_sql).lower()[long(str_where_pos):]
		result, col = oracle_fun.oracle_query(sql_undo_select, user, passwd, host, port, dbname)
		sql_colums="("
		for n in range(len(col)):
			sql_colums=sql_colums+col[n]+','
		sql_colums=sql_colums[:len(sql_colums)-1]+')'
		for m in range(len(result)):
			sql_temp='('
			for k in range(len(col)):
				sql_temp=sql_temp+result[m][k]+','
			sql_temp=str(sql_temp)[:len(sql_temp)-1]
			sql_undo='insert into '+sql_table+' '+sql_colums+'values '+sql_temp+');'
			list_sql_return.append(sql_undo)
	return list_sql_return,sql_table,sqltype


if __name__ == '__main__':
	results, col=backupdml_insert("update a set a.a=1,a.c=2 where a.a=123 and a.b='234'")