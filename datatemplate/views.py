#coding=UTF-8
from django.shortcuts import render,render_to_response
from datatemplate.form import DataTemplateMgr,AddForm
# from django.http import HttpResponse,HttpResponseRedirect,StreamingHttpResponse
from django.contrib.auth.decorators import login_required,permission_required
from myapp.include import function as func,sqlfilter
import datetime
from myapp.include import function as func,inception as incept,chart,pri,meta,sqlfilter
from myapp.tasks import task_run
from myapp.models import Task
# Create your views here.
@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_see_template_mgr', login_url='/')
def template_mgr(request):
    #objlist = func.get_mysql_hostlist(request.user.username, 'meta')
    # result = func.get_diff('mysql-lepus-test','mysql_replication','mysql-lepus','mysql_replication')
    # print result
    form = DataTemplateMgr(request.POST)
    if request.method == 'POST':
        if request.POST.has_key('query'):
            try:
                tmpname = request.POST['templatename_searched']
                datalist = func.get_template_dmldata(tmpname)
                return render(request, 'template_mgr.html',{'templatename_searched':tmpname,'form':form,'datalist':datalist})
            except Exception, e:
                return render(request, 'template_mgr.html', locals())
        # elif request.POST.has_key('check_tmp'):
        #     return render(request, 'template_mgr.html', locals())
        elif request.POST.has_key('create_tmp'):
            if form.is_valid():
                try:
                    form = DataTemplateMgr(request.POST)
                    templteno = request.POST['templteno']
                    templtename =request.POST['templtename']
                    templtestatus =request.POST['templtestatus']
                    templtememo =request.POST['templtememo']
                    create_user  = request.user.username
                    createtime = datetime.datetime.now()
                    a = form.cleaned_data['a']
                    form = DataTemplateMgr(initial={'a': a})
                    func.create_template(templteno,templtename,templtestatus,templtememo,create_user,createtime, a)
                    datalist = func.get_template_dmldata("")
                    info = "create template success!"
                    return render(request, 'template_mgr.html',{"info":info ,'datalist':datalist})
                except Exception, e:
                    info = "create template fail!"
                    return render(request, 'template_mgr.html', locals())
            else:
                return render(request, 'template_mgr.html', locals())
        elif request.POST.has_key('modify_tmp'):
            if form.is_valid():
                id=request.POST['id_template']
                templteno = request.POST['templteno']
                templtename = request.POST['templtename']
                templtestatus = request.POST['templtestatus']
                templtememo = request.POST['templtememo']
                create_user = request.user.username
                createtime = datetime.datetime.now()
                a = form.cleaned_data['a']
                form = DataTemplateMgr(initial={'a': a})
                try:
                    func.modify_template(id,templteno,templtename,templtememo,create_user,a,templtestatus)
                    datalist = func.get_template_dmldata("")
                    info = "modify template success"
                except Exception, e:
                    info = "modify template fail!"
                return render(request, 'template_mgr.html', {"info":info ,'datalist':datalist})
            else:
                return render(request, 'template_mgr.html', locals())
        elif request.POST.has_key('delete_tmp'):
            id = request.POST['id_template']
            try:
                flag=func.delete_template(id)
                if flag==-1:
                    info = "delete template failed,please choose!"
                else:
                    info = "delete template success"
                datalist = func.get_template_dmldata("")

            except Exception, e:
                info = "delete template fail!"
            return render(request, 'template_mgr.html',{"info":info ,'datalist':datalist})
        else:
            return render(request, 'template_mgr.html', locals())
    else:
        form = DataTemplateMgr()
    return render(request,'template_mgr.html', locals())

@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_see_template_dmldata', login_url='/')
def template_dmldata(request):
    #objlist = func.get_mysql_hostlist(request.user.username, 'meta')
    # result = func.get_diff('mysql-lepus-test','mysql_replication','mysql-lepus','mysql_replication')
    # print result
    form = AddForm(request.POST)
    objlist = func.get_mysql_hostlist(request.user.username, 'incept')
    templist = func.get_template_demo("")
    if request.method == 'POST':
        choosed_host = request.POST['dbhost']
        sqlmemo = request.POST['sqlmemo'][0:100]
        choosed_temp = request.POST['cx_temp']
        searchtempname= request.POST['searchtempname']
        if len(choosed_temp) == 0:
            return render(request, 'template_dmldata.html',
                          {"form": form, "objlist": objlist, 'choosed_host': choosed_host, "sqlmemo_val": sqlmemo,
                           "templist": templist, "cx_temp": choosed_temp
                              , "tmp_search": searchtempname})
        # if len(sqlmemo) == 0:
        #     form = AddForm(request.POST)
        #     status="Please input the memo"
        #     return render(request, 'template_dmldata.html',
        #                   {"form": form, "objlist": objlist,  'choosed_host': choosed_host,"sqlmemo_val":sqlmemo,"status":status,"templist":templist})
        if request.POST.has_key('check'):
            if form.is_valid():
                a = form.cleaned_data['a']
                try:
                    tmpsqltext = ''
                    for i in sqlfilter.get_sqldml_detail(sqlfilter.sql_init_filter(a), 2):
                        tmpsqltext = tmpsqltext + i
                    a = tmpsqltext
                    form = AddForm(initial={'a': a})
                except Exception, e:
                    pass

                data_mysql, collist, dbname = incept.inception_check(choosed_host, a, 2)
                # check the nee to split sqltext first

                if len(data_mysql) > 1:
                    split = 1
                    # return render(request, 'template_dmldata.html',
                    #               { "form": form,"objlist":objlist,"data_list":data_mysql,"collist":collist,"split":split, 'choosed_host': choosed_host,"sqlmemo_val":sqlmemo,"templist":templist})
                    return render(request, 'template_dmldata.html',
                                  {"form": form, "objlist": objlist, 'choosed_host': choosed_host,
                                   "sqlmemo_val": sqlmemo, "templist": templist, "cx_temp": choosed_temp
                                      , "tmp_search": searchtempname,"data_list":data_mysql,"collist":collist,"split":split})
                else:
                    data_mysql, collist, dbname = incept.inception_check(choosed_host, a)
                    # return render(request, 'template_dmldata.html',
                    #               { "form": form,"objlist":objlist,"data_list":data_mysql,"collist":collist, 'choosed_host': choosed_host,"sqlmemo_val":sqlmemo,"templist":templist})
                return render(request, 'template_dmldata.html',
                              {"form": form, "objlist": objlist, 'choosed_host': choosed_host,
                               "sqlmemo_val": sqlmemo, "templist": templist, "cx_temp": choosed_temp
                                  , "tmp_search": searchtempname,  "data_list": data_mysql,
                               "collist": collist})
            else:
                return render(request, 'template_dmldata.html', locals())
        elif request.POST.has_key('addsql'):
            needbackup =1
            if form.is_valid():
                sqltext = form.cleaned_data['a']
                # get valid statement
                try:
                    tmpsqltext = ''
                    for i in sqlfilter.get_sqldml_detail(sqlfilter.sql_init_filter(sqltext), 2):
                        tmpsqltext = tmpsqltext + i
                    sqltext = tmpsqltext
                    form = AddForm(initial={'a': sqltext})
                except Exception, e:
                    pass
                data_mysql, tmp_col, dbname = incept.inception_check(choosed_host, sqltext, 2)
                # check if the sqltext need to be splited before uploaded
                if len(data_mysql) > 1:
                    split = 1
                    status = 'UPLOAD  FAIL'
                    # return render(request, 'inception.html', {'form': form,
                    #                                           'objlist': objlist,
                    #                                           'status': status,
                    #                                           'split': split,
                    #                                           'choosed_host': choosed_host,"sqlmemo_val":sqlmemo})
                    return render(request, 'template_dmldata.html',
                                  {"form": form, "objlist": objlist, 'choosed_host': choosed_host, 'status': status,'split': split,
                                   "sqlmemo_val": sqlmemo, "templist": templist, "cx_temp": choosed_temp
                                      , "tmp_search": searchtempname,  "data_list": data_mysql})
                # check sqltext before uploaded
                else:
                    tmp_data, tmp_col, dbname = incept.inception_check(choosed_host, sqltext)
                    for i in tmp_data:
                        if int(i[2]) != 0:
                            status = 'UPLOAD TASK FAIL,CHECK NOT PASSED'
                            return render(request, 'template_dmldata.html', locals())
                specification="template_dml:"+sqlmemo;
                rstatus = 'check passed'
                myNewTask = incept.record_taskdml(request, sqltext, choosed_host, specification, needbackup,rstatus)
                nllflag = task_run(myNewTask.id, request)
                status = 'EXEC OK'
                datalist= Task.objects.filter(id=myNewTask.id).order_by("-create_time")[0:50]
                # sendmail_task.delay(choosed_host+'\n'+sqltext)
                #sendmail_task.delay(myNewTask)

                # return render(request, 'template_dmldata.html', {'form': form,
                #                                           'objlist': objlist,
                #                                           'status': status,
                #                                           'choosed_host': choosed_host,"datalist":datalist,"sqlmemo_val":sqlmemo})
                return render(request, 'template_dmldata.html',
                              {"form": form, "objlist": objlist, 'choosed_host': choosed_host, 'status': status,
                               "sqlmemo_val": sqlmemo, "templist": templist, "cx_temp": choosed_temp
                                  , "tmp_search": searchtempname, "data_list": data_mysql})
            else:
                status = 'EXEC  FAIL'
                return render(request, 'template_dmldata.html', {'form': form,
                                                          'objlist': objlist,
                                                          'status': status,
                                                          'choosed_host': choosed_host,"sqlmemo_val":sqlmemo})
            form = AddForm()
            return render(request, 'template_dmldata.html', {'form': form,
                                                  'upform': upform,
                                                  'objlist': objlist,
                                                  'choosed_host': choosed_host,"sqlmemo_val":sqlmemo})
            return render(request, 'template_dmldata.html', locals())
        elif request.POST.has_key('searchtmp'):
            templist = func.get_template_demo(searchtempname)
            return render(request, 'template_dmldata.html', {"form": form, "objlist": objlist,  'choosed_host': choosed_host,"sqlmemo_val":sqlmemo,"templist":templist,"cx_temp":choosed_temp
                                                             ,"tmp_search":searchtempname})
        elif request.POST.has_key('committmp'):
            temp_no=str(choosed_temp).split(",")[0]
            tempdetail=func.get_template_data_by_tmp_no(temp_no)
            row=tempdetail[0]
            v_sqltext=row.sqltext
            sqlmemo=row.templtememo
            form = AddForm(initial={'a': v_sqltext})
            return render(request, 'template_dmldata.html', {"form": form, "objlist": objlist,  'choosed_host': choosed_host,"sqlmemo_val":sqlmemo,"templist":templist,"cx_temp":choosed_temp
                                                             ,"tmp_search":searchtempname,"sqlmemo_val":sqlmemo})
        else:
            return render(request, 'template_dmldata.html',locals())
    else:
        return render(request, 'template_dmldata.html', locals())
