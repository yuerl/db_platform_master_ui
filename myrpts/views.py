from django.shortcuts import render
from monitor.models import MysqlStatus,Mysql_replication
from myapp.models import Db_account,Db_instance,MySQL_monitor
from django.http import HttpResponse,HttpResponseRedirect,StreamingHttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required,permission_required
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from django.contrib.auth.models import User
from myapp.form import sqldForm,BeginEndTime
# Create your views here.
@login_required(login_url='/accounts/login/')
def rpt_sql(request):

    if request.method == 'POST':
        formtime = BeginEndTime(request.POST)
        formsql = sqldForm(request.POST)
        if request.POST.has_key('query'):
            try:
                proname = request.POST['proname_search']
                datalist = func.get_pro_data(proname)
                return render(request, 'script_project_mgr.html',{'proname_searched':proname,'form':form,'datalist':datalist})
            except Exception, e:
                return render(request, 'script_project_mgr.html', locals())
        elif request.POST.has_key('create_pro'):
            try:
                prono = request.POST['prono_mgr']
                proname = request.POST['proname_mgr']
                user_mgr = request.POST['user_mgr']
                status = request.POST['status_mgr']
                user = request.user.username
                createtime = request.POST['begin']
                func.create_pro(prono,proname,user_mgr,status,user,createtime)
                datalist = func.get_pro_data("")
                info = "create project success!"
                return render(request, 'script_project_mgr.html', locals())
            except Exception, e:
                info = "create project fail!"
                return render(request, 'script_project_mgr.html', locals())
        elif request.POST.has_key('modify_pro'):
            id=request.POST['id_mgr']
            prono = request.POST['prono_mgr']
            proname = request.POST['proname_mgr']
            user_mgr = request.POST['user_mgr']
            status = request.POST['status_mgr']
            try:
                func.modify_pro(id,prono,proname,user_mgr,status)
                datalist = func.get_pro_data("")
                info = "modify project success"
            except Exception, e:
                info = "modify project fail!"
            return render(request, 'script_project_mgr.html', locals())
        elif request.POST.has_key('delete_pro'):
            id = request.POST['id_mgr']
            try:
                flag=func.delete_pro(id)
                if flag==-1:
                    info = "delete project failed,please choose!"
                else:
                    info = "delete project success"
                datalist = func.get_pro_data("")

            except Exception, e:
                info = "delete project fail!"
            return render(request, 'script_project_mgr.html', locals())
        elif request.POST.has_key('build_script'):
            id = request.POST['build_script']
            result_msg=func.makescripts(id)
            datalist = func.get_pro_data_byid(id)
            proname_searched = datalist[0].proname
            return render(request, 'script_project_mgr.html', {"datalist":datalist,"proname_searched":proname_searched,"info":result_msg})
        else:
            return render(request, 'rpt_sql.html',  {'formtime':formtime,'formsql':formsql})
    else:
        formtime = BeginEndTime( )
        formsql = sqldForm( )
    return render(request,'rpt_sql.html', {'formtime':formtime,'formsql':formsql})






# @login_required(login_url='/accounts/login/')
# @permission_required('myapp.can_see_mysqladmin', login_url='/')
# def test_tb(request):
#     dbtag = request.GET['dbtag']
#     if dbtag!='all':
#         mydata = {'dupresult':get_dupreport(dbtag,request.GET['email'])}
#     # return render(request, 'batch_add.html', locals())
#     return JsonResponse(mydata)

