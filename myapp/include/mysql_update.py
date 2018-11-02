#!/usr/bin/python
# -*- coding: utf-8 -*-
#废弃
import os
from datetime import datetime
#读取文件内容写入目标文件中
def readFile(source,target,error_log):
    update_str = datetime.now().strftime('%Y%m%d%H%M%S')
    fopen = open(source, 'r')
    appen_str="DELIMITER ??"+"\r\n"+"DROP PROCEDURE IF EXISTS schema_change??"+"\r\n"+"CREATE PROCEDURE schema_change()"+"\r\n"+"BEGIN";
    #提取的表名字
    stable = "";
    #是否crete table和altertable的标志
    newobj_flag=0;
    #报错字段的列表
    list_item = []
    for eachLine in fopen:
        eachLine=eachLine.strip()
        if len(eachLine)>0:
            lower_str=eachLine.lower()
            if lower_str.find("#") == 0:
                pass
            elif lower_str.find("--") == 0:
                pass
            elif lower_str.find("select") ==0:
                newobj_flag=0
            elif lower_str.find("create") ==0:
                try:
                    if len(list_item) > 0:
                        str = "(";
                        for i in list_item:
                            str = str + "'" + i + "'" + ","
                        str = str[0:len(str) - 1] + ")"
                        appen_str = appen_str.replace("('@!@')" , str)
                    list_item = []
                    #是否新建立了一个表，标志create或者alter表
                    newobj_flag = 1
                    itemstail = ["add","change","drop","("]
                    itemshead = ["create", "table"]
                    replace_str =["create","table","TABLE","CREATE","`"]
                    str_temp=""
                    flag = 0
                    for item in itemstail:
                        if lower_str.find(item)>-1:
                            str_temp=lower_str[0:lower_str.find(item)]
                            for head in itemshead:
                                if lower_str.find(head) >-1:
                                    stable=str_temp[lower_str.find(head):]
                                    for rep in replace_str:
                                        stable = stable.replace(rep, "").strip()
                                    flag=1
                    if flag==0:
                        stable = lower_str
                        for rep in replace_str:
                            stable = stable.replace(rep, "").strip()
                    appen_str = appen_str +"\r\n"+ "IF NOT EXISTS (SELECT * FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = '"+stable+"' ) THEN"+"\r\n" + eachLine;
                except Exception, e:
                    writeFile(error_log, "illegal create " + eachLine)
            elif lower_str.find("alter") ==0:
                 try:
                    #新表开始前，对字段进行替换
                    if len(list_item) > 0:
                        str = "(";
                        for i in list_item:
                            str = str + "'" + i + "'" + ","
                        str = str[0:len(str) - 1] + ")"
                        appen_str = appen_str.replace("('@!@')", str)
                    list_item = []
                    newobj_flag = 1
                    itemstail = ["add ", "change ", "drop ", " ("]
                    itemshead = ["alter", "table"]
                    replace_str=["alter","table","TABLE","ALTER","`"]
                    str_temp = ""
                    flag = 0
                    for item in itemstail:
                        if lower_str.find(item) > -1:
                            str_temp = lower_str[0:lower_str.find(item)]
                            for head in itemshead:
                                if lower_str.find(head) > -1:
                                    stable = str_temp[lower_str.find(head):]
                                    for rep in replace_str:
                                        stable=stable.replace(rep,"").strip()
                                    flag=1
                    if flag==0:
                        stable=lower_str
                        for rep in replace_str:
                            stable = stable.replace(rep, "").strip()
                    appen_str = appen_str + "\r\n" + "IF NOT EXISTS (SELECT * FROM information_schema.columns WHERE table_schema = DATABASE() AND table_name = '"+ stable + "' and COLUMN_NAME IN  ('@!@')  ) THEN" + "\r\n" + eachLine;
                 except Exception, e:
                     writeFile(error_log, "illegal alter " + eachLine)
            else:
                if lower_str.find("insert") > -1 or lower_str.find("update") > -1 or lower_str.find("delete") > -1:
                    newobj_flag = 0
                    if lower_str.find("insert") >-1:
                        try:
                            insert_table=lower_str[0:lower_str.index("(")].replace("insert","").replace("into","").strip()
                            insert_right=lower_str[lower_str.index("("):]
                            insert_key=insert_right[0:insert_right.index(",")].replace("(","").replace(")","").replace("values","")
                            insert_values=insert_right[insert_right.find(")values("):].replace("(","").replace(")","").replace("values","")
                            insert_values_key=insert_values[0:insert_values.index(",")]
                            appen_str=appen_str+"\r\n"+"IF NOT EXISTS (SELECT * FROM "+insert_table+" WHERE "+insert_key+" = "+insert_values_key+" ) THEN"
                            appen_str = appen_str + "\r\n" + eachLine + "\r\n" + "ELSE" + "\r\n" + "SELECT \"ERROR 1050 (42S01): Table " + insert_table +" Primary Key"+insert_values_key +" already exists\"   AS \"ERROR MSG\" ;"
                            appen_str = appen_str+"\r\n"+"insert into dba_update_log(update_no,update_status,msg,create_time)values("
                            appen_str = appen_str +"'"+ update_str+"'"+",'error','Table "+insert_table+"INSERT Primary Key"+insert_values_key.replace("'","").replace(";","") +" already exists'"+',now()'+");"
                            appen_str=appen_str+  "\r\n" + "END IF;"
                        except Exception, e:
                            writeFile(error_log,"illegal insert "+eachLine)
                    elif lower_str.find("update")>-1:
                        try:
                            update_where =lower_str[lower_str.find(" where "):]
                            update_table=lower_str[0:lower_str.index(" set ")].replace("update").strip()
                            appen_str = appen_str + "\r\n" + "IF  EXISTS (SELECT * FROM " + update_table + "   " + update_where.replace(";","") + " ) THEN"
                            appen_str = appen_str + "\r\n" + eachLine + "\r\n" + "ELSE" + "\r\n" + "SELECT \"ERROR 1050 (42S01): Table " + update_table + " Where case" + update_where + " already exists\"   AS \"ERROR MSG\" ;"
                            appen_str = appen_str + "\r\n" + "insert into dba_update_log(update_no,update_status,msg,create_time)values("
                            appen_str = appen_str + "'" + update_str + "'" + ",'error','Table " + update_table + "UPDATE Where case" + update_where.replace("'").replace(";","") + " not exists'" + ',now()' + ");"
                            appen_str = appen_str + "\r\n" + "END IF;"
                        except Exception, e:
                            writeFile(error_log,"illegal update "+eachLine)
                    elif lower_str.find("delete") > -1:
                        try:
                            delete_where=lower_str[lower_str.find(" where "):]
                            delete_table = lower_str[0:lower_str.find(" where ")].replace("delete","").replace("from","").strip()
                            appen_str = appen_str + "\r\n" + "IF  EXISTS (SELECT * FROM " + delete_table + "   " + delete_where.replace(";","") + " ) THEN"
                            appen_str = appen_str + "\r\n" + eachLine + "\r\n" + "ELSE" + "\r\n" + "SELECT \"ERROR 1050 (42S01): Table " + delete_table + " Where case" + delete_where + " already exists\"   AS \"ERROR MSG\" ;"
                            appen_str = appen_str + "\r\n" + "insert into dba_update_log(update_no,update_status,msg,create_time)values("
                            appen_str = appen_str + "'" + update_str + "'" + ",'error','Table " + delete_table + "DELETE Where case" + delete_where.replace("'","").replace(";","") + " not exists'" + ',now()' + ");"
                            appen_str = appen_str + "\r\n" + "END IF;"
                        except Exception, e:
                            writeFile(error_log,"illegal delete "+eachLine)
                    #appen_str = appen_str +"\r\n"+eachLine
                else:
                    this_flag=0
                    if lower_str.strip().find(";") + 1 == len(lower_str.strip()):
                        this_flag=1
                        appen_str = appen_str + "\r\n" + eachLine + "\r\n" + "ELSE" + "\r\n" + "SELECT \"ERROR 1050 (42S01): Table " + stable + "  Table or Column already exists\"   AS \"ERROR MSG\" ;"
                        appen_str = appen_str+"\r\n"+"insert into dba_update_log(update_no,update_status,msg,create_time)values("
                        appen_str = appen_str +"'"+ update_str+"'"+",'error','Table "+stable+" Table or Column already exists'"+',now()'+");"
                        appen_str=appen_str+  "\r\n" + "END IF;"
                    else:
                        appen_str = appen_str + "\r\n" + eachLine
                    ddl_timetail=[" tinyint("," int("," varchar("," bigint("," bit("," datetime"," date"," decimal("]
                    ddl_replace=["add ","change ","column "]
                    if newobj_flag == 1:
                        temp_str=eachLine.lower().strip()
                        if temp_str.find("change")==0:
                            pass
                        else:
                            for tail in ddl_timetail:
                                temp_str=temp_str.replace("`","").strip()
                                if temp_str.find(tail) >-1:
                                    temp_str=temp_str[0:temp_str.find(tail)]
                                for rep in ddl_replace:
                                    temp_str=temp_str.replace("`","").strip()
                                    temp_str = temp_str.replace(rep, "")
                            if len(temp_str)>0:
                                list_item.append(temp_str)
                    if this_flag==1:
                        newobj_flag = 0
            # writeFile(target,eachLine)
    fopen.close()
    appen_str=appen_str+"\r\n"+"END??"+"\r\n"+"DELIMITER ;"+"\r\n"+"CALL schema_change();"
    writeFile(target,appen_str);
#根据文件名字写入字符串，自动前面加回车换行
def writeFile(filename,str):
    fopen = open(filename, 'w')
    fopen.write('%s' % ("\r\n"+str))
    fopen.close()

#格式化读取的行数据,


if __name__ == '__main__':
    source = "/opt/dev/scripts/update.sql"
    target = "/opt/dev/scripts/mysql_update.sql"
    error_log= "/opt/dev/scripts/mysql_update.log"
    readFile(source,target,error_log)
    host = '/opt/mysql5639/bin/mysql  -uroot -p123321 -Dfintech < /opt/dev/scripts/mysql_update.sql '
    p = os.popen(host)
    for line in p.readlines():
        print line