import MySQLdb,sys,string,time,datetime,uuid
from django.contrib.auth.models import User
from myapp.models import Db_name,Db_account,Db_instance,Oper_log,Task
from myapp.form import LoginForm,Captcha
from django.db.models import Count
from myapp.include import function as func,meta

def get_main_chart():
    log = Oper_log.objects.values('sqltype').annotate(num=Count('sqltype')).order_by("-num")
    collist=[]
    datalist = []
    for i in log:
        collist.append(i['sqltype'])
        datalist.append(i['num'])
    return datalist,collist


def get_task_chart():
    #today
    log = Task.objects.filter(create_time__gte=datetime.date.today()).values('status').annotate(num=Count('status')).order_by("-num")
    collist=[]
    datalist = []
    for i in log:
        collist.append(i['status'])
        datalist.append(i['num'])
    return datalist,collist

#'executed','executed failed','check not passed','check passed','running'

def get_task_bingtu():
    log = Task.objects.values('status').annotate(num=Count('status')).order_by("-num")
    collist=[]
    datalist = []
    for i in log:
        dict={}
        dict['value'] =i['num']
        dict['name'] = i['status']
        datalist.append(dict)
    return datalist

def get_task_bingtu90days():
    log = Task.objects.filter(create_time__gte=datetime.date.today()- datetime.timedelta(days=90) ).values('status').annotate(num=Count('status')).order_by("-num")
    collist=[]
    datalist = []
    for i in log:
        dict={}
        # dict['value'] =i['num']
        # dict['name'] = i['status']
        dict['label'] = i['status']
        dict['data'] = i['num']
        datalist.append(dict)
    return datalist

def get_task_bingtu7days():
    #today
    log = Task.objects.filter(create_time__gte=datetime.date.today()- datetime.timedelta(days=7) ).values('status').annotate(num=Count('status')).order_by("-num")
    collist = []
    datalist = []
    for i in log:
        dict = {}
        # dict['value'] =i['num']
        # dict['name'] = i['status']
        dict['label'] = i['status']
        dict['data'] = i['num']
        datalist.append(dict)
    return datalist


def get_main_chart7days_data():
    data=func.get_main_chart(0)
    collist=[]
    datalist = []
    for i in data:
        dict = {}
        dict['y'] = i[1]
        dict['x'] = i[0]
        datalist.append(dict)
    return datalist

def get_main_chart7days_db():
    data=func.get_main_chart(1)
    collist=[]
    datalist = []
    for i in data:
        dict = {}
        dict['y'] = i[1]
        dict['x'] = i[0]
        datalist.append(dict)
    return datalist

def get_inc_usedrate():
    results,col = meta.get_his_meta('all', 6)
    collist = []
    datalist = []
    for i in results:
        try:
            collist.append(i[2]+ "\n"+ i[0])
            datalist.append(int(i[1]))
        except Exception,e:
            pass
    return datalist, collist