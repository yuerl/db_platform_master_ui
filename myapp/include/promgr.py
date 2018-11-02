#!/bin/env python
#-*-coding:utf-8-*-
import MySQLdb,sys,string,time,datetime,uuid,commands,os
from myapp.include.encrypt import prpcrypt
from django.contrib.auth.models import User,Permission,ContentType,Group
from myapp.models import Db_name,Db_account,Db_instance,Oper_log,Login_log,Db_group
from myapp.form import LoginForm,Captcha
from myapp.etc import config
from mypro import settings
from django.db import connection
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
            # for row in Db_name.objects.all().order_by("dbtag"):
            #     #find the account which is admin
            #     if row.db_account_set.all().filter(role='admin'):
            #         if row.instance.filter(role__in=['write','all','read']).filter(db_type=dbtype):
            #             host_list.append(row.dbtag)
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
