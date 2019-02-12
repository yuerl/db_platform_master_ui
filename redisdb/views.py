#coding=UTF-8
from django.shortcuts import render,render_to_response
from myapp.form import AddForm
# from django.http import HttpResponse,HttpResponseRedirect,StreamingHttpResponse
import pyredis
from django.contrib.auth.decorators import login_required,permission_required
from myapp.include import function as func


# Create your views here.
@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_see_redis_menu_redis_query', login_url='/')
def redis_query(request):
    try:
        favword = request.COOKIES['myfavword']
    except Exception,e:
        pass
    dblist = pyredis.get_redisdb_list(request.user.username)
    typelist=[]
    typelist.append("get(name)")
    typelist.append("mget(keys, *args)")
    typelist.append("getrange(key, start, end)")
    typelist.append("getbit(name, offset)")
    typelist.append("strlen(name)")
    typelist.append("hget(name,key)")
    typelist.append("hgetall(name)")
    typelist.append("hmget(name, keys, *args)")
    typelist.append("hlen(name)")
    typelist.append("hkeys(name)")
    typelist.append("hvals(name)")
    typelist.append("hexists(name, key)")
    typelist.append("lindex(name, index)")
    typelist.append("lrange(name, start, end)")
    typelist.append("exists(name)")
    typelist.append("scard(name)")
    typelist.append("smembers(name)")
    typelist.append("sdiff(keys, *args)")
    typelist.append("sunion(keys, *args)")
    typelist.append("zcard(name)")
    typelist.append("zcount(name, min, max)")


    #dblist = ['ymmSmsLogYm','table2','table3','table4']
    if request.method == 'POST' :
        form = AddForm(request.POST)

            #instancetag = request.POST['instancetag']
        choosedb = request.POST['choosedb']
        #tblist = pyredis.get_redis_collection(choosedb, request.user.username)
        try:
            if request.POST.has_key('query'):
                #return HttpResponse(tablename)
                cmdtype = request.POST['cmdtype']
                if form.is_valid():
                    a = form.cleaned_data['a']
                    func.log_redis_op(a,choosedb,request)
                    msg="error"
                    data_list,msg = pyredis.get_redis_data(a, choosedb, request.user.username,cmdtype)
                # print data_list
                return render(request,'redisdb_query.html',locals())
            else:
                return render(request, 'redisdb_query.html', locals())
            # elif request.POST.has_key('dbinfo'):
            #     #del tblist
            #     info = pyredis.get_db_info(choosedb, request.user.username)
            #     return render(request, 'redisdb_query.html', locals())
            # elif request.POST.has_key('tbinfo'):
            #     choosed_tb = request.POST['choosed_tb']
            #     info = pyredis.get_tb_info(choosedb,choosed_tb, request.user.username)
            #     return render(request, 'redisdb_query.html', locals())
            # elif request.POST.has_key('tbindexinfo'):
            #     choosed_tb = request.POST['choosed_tb']
            #     indinfo = pyredis.get_tbindex_info(choosedb, choosed_tb, request.user.username)
            #     # print info
            #     return render(request, 'redisdb_query.html', locals())

                # return render(request,'redisdb_query.html',{'form': form,'data_list':data_mongo,'col':"record",'tablelist':table_list,'choosed_table':tablename})
        except Exception,e:
            print e
            return render(request, 'redisdb_query.html', locals())
            #else:
                #return render(request, 'mongo_query.html', {'form': form })
        # else:
        #     print "not valid"
        #     return render(request, 'redisdb_query.html', locals())
    else:
        form = AddForm()
        return render(request, 'redisdb_query.html', locals())

@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_see_redisdb_command', login_url='/')
def redis_command(request):
    return render(request, 'redisdb_command.html', locals())