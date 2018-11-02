#coding=UTF-8
import MySQLdb,sys,string,time,datetime,uuid,json
from django.contrib.auth.models import User
from myapp.models import Db_name,Db_account,Db_instance
from myapp.etc import config
from django.core.serializers.json import DjangoJSONEncoder
from myapp.include.encrypt import prpcrypt
import redis
public_user = config.public_user
export_limit = int(config.export_limit)
def get_redisdb_list(username,tag='tag',search=''):
    dbtype='redis'
    host_list = []
    if len(search) ==0:
        if (tag=='tag'):
            a = User.objects.get(username=username)
            #如果没有对应role='read'或者role='all'的account账号，则不显示在下拉菜单中
            #print a.db_name_set.all().order_by("dbtag").query
            for row in a.db_name_set.all().order_by("dbtag"):
                if row.db_account_set.all().filter(role__in=['read','all']):
                    if row.instance.all().filter(role__in=['read','all']).filter(db_type=dbtype):
                        #print row.instance.all().filter(role__in=['read','all']).query
                        host_list.append(row.dbtag)
        elif (tag=='log'):
            for row in Db_name.objects.values('dbtag').distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif (tag=='exec'):
            a = User.objects.get(username=username)
            #如果没有对应role='write'或者role='all'的account账号，则不显示在下拉菜单中
            for row in a.db_name_set.all().order_by("dbtag"):
                if row.db_account_set.all().filter(role__in=['write','all']):
            #排除只读实例
                    if row.instance.all().filter(role__in=['write','all']).filter(db_type=dbtype):
                        host_list.append(row.dbtag)
    elif len(search) > 0:
        if (tag=='tag'):
            a = User.objects.get(username=username)
            #如果没有对应role='read'或者role='all'的account账号，则不显示在下拉菜单中
            for row in a.db_name_set.filter(dbname__contains=search).order_by("dbtag"):
                if row.db_account_set.all().filter(role__in=['read','all']):
                    if row.instance.all().filter(role__in=['read','all']).filter(db_type=dbtype):
                        host_list.append(row.dbtag)
        elif (tag=='log'):
            for row in Db_name.objects.values('dbtag').distinct().order_by("dbtag"):
                host_list.append(row['dbtag'])
        elif (tag=='exec'):
            a = User.objects.get(username=username)
            #如果没有对应role='write'或者role='all'的account账号，则不显示在下拉菜单中
            for row in a.db_name_set.filter(dbname__contains=search).order_by("dbtag"):
                if row.db_account_set.all().filter(role__in=['write','all']):
            #排除只读实例
                    if row.instance.all().filter(role__in=['write','all']).filter(db_type=dbtype):
                        host_list.append(row.dbtag)
    return host_list


def get_redis_coninfo(hosttag,useraccount):

    a = Db_name.objects.filter(dbtag=hosttag)[0]
    # a = Db_name.objects.get(dbtag=hosttag)
    tar_dbname = a.dbname
    try:
        if a.instance.all().filter(role='read')[0]:
            tar_host = a.instance.all().filter(role='read')[0].ip
            tar_port = a.instance.all().filter(role='read')[0].port
    # 如果没有设置或没有role=read，则选择第一个读到的all实例读取
    except Exception, e:
        tar_host = a.instance.filter(role='all')[0].ip
        tar_port = a.instance.filter(role='all')[0].port
        # tar_host = a.instance.all()[0].ip
        # tar_port = a.instance.all()[0].port
    for i in a.db_account_set.all():
        if i.role != 'write' and i.role != 'admin':
            # find the specified account for the user
            if i.account.all().filter(username=useraccount):
                tar_username = i.user
                tar_passwd = i.passwd
                break
    # not find specified account for the user ,specified the public account to the user
    if not vars().has_key('tar_username'):
        for i in a.db_account_set.all():
            if i.role != 'write' and i.role != 'admin':
                # find the specified account for the user
                if i.account.all().filter(username=public_user):
                    tar_username = i.user
                    tar_passwd = i.passwd
                    break
    pc = prpcrypt()
    return tar_host,tar_port,tar_username,pc.decrypt(tar_passwd),tar_dbname


def get_db_info(hosttag,useraccount):
    tar_host, tar_port, tar_username, tar_passwd, tar_dbname = get_redis_coninfo(hosttag, useraccount)

    if tar_passwd<>"null":
        connect = redis.Connection(host=tar_host, port=int(tar_port), db=int(tar_dbname), password=tar_passwd,decode_responses=True)
    else:
        connect = redis.Connection(host=tar_host, port=int(tar_port),db=int(tar_dbname), decode_responses=True)
    #connect = redis.Redis(host=tar_host,port=int(tar_port),password=tar_passwd,decode_responses=True)
    results = connect.execute_command({'info': 1})
    return results

def get_tb_info(hosttag,tbname,useraccount):
    tar_host, tar_port, tar_username, tar_passwd, tar_dbname = get_redis_coninfo(hosttag, useraccount)
    connect = redis.Redis(tar_host, int(tar_port))
    db = connect[tar_dbname]
    try:
        db.authenticate(tar_username, tar_passwd)
    except Exception, e:
        pass
    results = db.command({'collstats': tbname})
    return results

def get_tbindex_info(hosttag,tbname,useraccount):
    tar_host, tar_port, tar_username, tar_passwd, tar_dbname = get_redis_coninfo(hosttag, useraccount)
    pool = redis.Connection(host=tar_host,port=int(tar_port),password=tar_passwd,decode_responses=True)
    connect = redis
    db = connect[tar_dbname]
    try:
        db.authenticate(tar_username, tar_passwd)
    except Exception, e:
        pass
    collection = db[tbname]
    results = collection.index_information()
    return results

def get_redis_collection(hosttag,useraccount):
    try:
        tar_host, tar_port, tar_username, tar_passwd, tar_dbname = get_redis_coninfo(hosttag, useraccount)
        # 此处根据tablename获取其他信息
        if tar_passwd <> "null":
            pool = redis.ConnectionPool(host=tar_host, port=int(tar_port), db=int(tar_dbname), password=tar_passwd,
                                       decode_responses=True)

        else:
            pool = redis.ConnectionPool(host=tar_host, port=int(tar_port), password=tar_passwd,
                                        decode_responses=True)

        try:
            #rds_con=redis.Redis(connection_pool=pool)
            rds_con = redis.Redis(connection_pool=pool)
            results = rds_con.get("info")
        except Exception, e:
            pass
        #results = rds_con.get("info")
    except Exception, e:
        results,col = ([str(e)],''),['error']
    return results


def get_redis_data(b,hosttag,useraccount,cmdtype):
    try:
        tar_host, tar_port, tar_username, tar_passwd, tar_dbname = get_redis_coninfo(hosttag, useraccount)
        #此处根据tablename获取其他信息
        if tar_passwd <> "null":
            pool = redis.ConnectionPool(host=tar_host, port=int(tar_port), db=int(tar_dbname), password=tar_passwd,
                                       decode_responses=True)

        else:
            pool = redis.ConnectionPool(host=tar_host, port=int(tar_port), password=tar_passwd,
                                        decode_responses=True)
        try:
            redis_con=redis.Redis(connection_pool=pool)
            if cmdtype=="get(name)":
                # b=str(b)
                # b=b.strip()[:-1]
                # print(b)
                # b=str(b).replace("get(","")
                resulta=redis_con.get(b.encode('utf-8'))
            elif cmdtype=="mget(keys, *args)":
                # b = str(b)
                # b = b.strip()[:-1]
                # b = str(b).replace("mget(","")
                list=str(b).strip(',').split(',')
                # for i in list:
                #     if list.index(i)==len(list)-1:
                #         scommand =scommand+i
                #     else:
                #         scommand=scommand+i +','
                resulta = redis_con.mget(list)
            elif cmdtype == "getrange(key, start, end)":
                list = str(b).strip(',').split(',')
                resulta = redis_con.getrange(list[0],list[1],list[2])
            elif cmdtype == "getbit(name, offset)":
                list = str(b).strip(',').split(',')
                resulta = redis_con.getbit(list[0],list[1])
            elif cmdtype == "strlen(name)":
                resulta = redis_con.strlen(b)
            elif cmdtype == "hget(name,key)":
                list = str(b).strip(',').split(',')
                resulta = redis_con.hget(list[0],list[1])
            elif cmdtype == "hgetall(name)":
                resulta = redis_con.hgetall(b)
            elif cmdtype == "hmget(name, keys, *args)":
                list = str(b).strip(',').split(',')
                name=list[0]
                del list[0]
                resulta = redis_con.hmget(name,list)
            elif cmdtype == "hlen(name)":
                resulta = redis_con.hlen(b)
            elif cmdtype == "hkeys(name)":
                resulta = redis_con.hkeys(b)
            elif cmdtype == "hvals(name)":
                resulta = redis_con.hvals(b)
            elif cmdtype == "hexists(name, key)":
                list = str(b).strip(',').split(',')
                resulta = redis_con.hvals(list[0],list[1])
            elif cmdtype == "lindex(name, index)":
                list = str(b).strip(',').split(',')
                resulta = redis_con.lindex(list[0],list[1])
            elif cmdtype == "lrange(name, start, end)":
                list = str(b).strip(',').split(',')
                resulta = redis_con.lrange(list[0],list[1],list[2])
            elif cmdtype == "exists(name)":
                resulta = redis_con.exists(b)
            elif cmdtype == "scard(name)":
                resulta = redis_con.scard(b)
            elif cmdtype == "smembers(name)":
                resulta = redis_con.smembers(b)
            elif cmdtype == "sdiff(keys, *args)":
                list = str(b).strip(',').split(',')
                name = list[0]
                del list[0]
                resulta = redis_con.sdiff(name, list)
            elif cmdtype == "sunion(keys, *args)":
                list = str(b).strip(',').split(',')
                name = list[0]
                del list[0]
                resulta = redis_con.sunion(name, list)
            elif cmdtype == "zcard(name)":
                resulta = redis_con.zcard(b)
            elif cmdtype == "zcount(name, min, max)":
                list = str(b).strip(',').split(',')
                name = list[0]
                del list[0]
                resulta = redis_con.sunion(name, list)
            else:
                resulta="eror"
        except Exception,e:
            pass
        #tablename = tablename
        #collection = db[tbname]
        #a = '''{'currTime': 1477371861706}'''
        #resulta = collection.find(eval(b),{"_id":0}).limit(num)
        # resulta = collection.find().limit(20)
        #results = db.collection_names()    #获取所有tables名字
        results = []
        if str(type(resulta))=="<type 'list'>":
            for record in resulta:
                #resultdict = {}
                #for k,v in recordjson:
                #    resultdict[k] = v.encode('gb18030')    #["ObjectId('580ee6e6f3de9821b20e57db') is not JSON serializable"]
                results.append(record)
                #results.append(recordjson)
            msg="sucess"
        else:
            results.append(resulta)
            msg="sucess"
    except Exception, e:
        msg=e.message
        results = (['error'],'')
    return results,msg

#if __name__ == '__main__':
    #x="insert /*sdfs*/into mysql.test ;truncate table mysql.db;rename mysql.db ;rename asdf;delete from  `msql`.sa set ;delete ignore from t1 mysql.test values sdasdf;insert into ysql.user values()"
    # print x
    #x=" /*! */; select /**/ #asdfasdf; \nfrom mysql_replication_history;"
    #x = " insert into item_infor (id,name) values(7,'t\\'e\"st');drop t * from test;"

    #print  get_mongo_data('{"_class" : "com.mongodb.BasicDBObject"}','mongodb-easemob','message','root')