from django.shortcuts import render
from myapp.models import Task
from myapp.tasks import task_run
from django.contrib.auth.decorators import login_required, permission_required
from myapp.form import AddForm
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse, JsonResponse
from oracle import oracle_fun
from myapp.include import sqlfilter, function as func
from django.contrib.auth.models import User
from myapp.include import function as func, inception as incept, chart, pri, meta, sqlfilter
import csv


# Create your views here.
# table structure
class Echo(object):
	"""An object that implements just the write method of the file-like interface.
	"""

	def write(self, value):
		"""Write the value by returning it, instead of storing in a buffer."""
		return value


'''
def some_streaming_csv_view(request):
    """A view that streams a large CSV file."""
    # Generate a sequence of rows. The range is based on the maximum number of
    # rows that can be handled by a single sheet in most spreadsheet
    # applications.
    data = (["Row {}".format(idx), str(idx)] for idx in range(65536))
    pseudo_buffer = Echo()
    writer = csv.writer(pseudo_buffer)
    response = StreamingHttpResponse((writer.writerow(row) for row in data),
                                     content_type="text/csv")
    response['Content-Disposition'] = 'attachment; filename="test.csv"'
    return response
'''


@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_see_oracle_menu_oracle_query', login_url='/')
def oracle_query(request):
	# print request.user.username
	# print request.user.has_perm('myapp.can_oracle_query')
	try:
		favword = request.COOKIES['myfavword']
	except Exception, e:
		pass
	objlist = oracle_fun.get_oracle_hostlist(request.user.username)
	if request.method == 'POST':
		form = AddForm(request.POST)
		# request.session['myfavword'] = request.POST['favword']
		choosed_host = request.POST['cx']

		if not User.objects.get(username=request.user.username).db_name_set.filter(dbtag=choosed_host)[:1]:
			return HttpResponseRedirect("/")

		if request.POST.has_key('searchdb'):
			db_se = request.POST['searchdbname']
			objlist_tmp = oracle_fun.get_oracle_hostlist(request.user.username, 'tag', db_se)
			# incase not found any db
			if len(objlist_tmp) > 0:
				objlist = objlist_tmp

		if form.is_valid():
			a = form.cleaned_data['a']
			# get first valid statement
			try:
				# print func.sql_init_filter(a)
				a = sqlfilter.get_sql_detail(sqlfilter.sql_init_filter(a), 1)[0]
			except Exception, e:
				a = 'wrong'
				pass
			try:
				# show explain
				if request.POST.has_key('explain'):

					a = oracle_fun.check_explain(a)
					(data_list, collist, dbname) = oracle_fun.get_oracle_explain_data(choosed_host, a,
					                                                                  request.user.username, request,
					                                                                  100)
					return render(request, 'oracle_query.html',
					              {'form': form, 'objlist': objlist, 'data_list': data_list, 'collist': collist,
					               'choosed_host': choosed_host, 'dbname': dbname})
				#export csv
				elif request.POST.has_key('export') and request.user.has_perm('myapp.can_export'):
					# check if table in black list and if user has permit to query

					# inBlackList, blacktb = bc.Sqlparse(a).check_query_table(choosed_host,request.user.username)
					inBlackList, blacktb = func.mysql_blacklist_tb(a, request.user.username, choosed_host)
					if inBlackList:
						return render(request, 'oracle_query.html', locals())

					# a, numlimit = func.check_oracle_query(a, request.user.username, 'export')
					a, numlimit = oracle_fun.check_oracle_query(a, request.user.username)
					(data_list, collist, dbname) =  oracle_fun.get_oracle_data(choosed_host, a, request.user.username,
					                                                          request,
					                                                          numlimit)
					pseudo_buffer = Echo()
					writer = csv.writer(pseudo_buffer)
					# csvdata =  (collist,'')+data_mysql
					i = 0
					results_long = len(data_list)
					results_list = [None] * results_long
					for i in range(results_long):
						results_list[i] = list(data_list[i])
					results_list.insert(0, collist)
					a = u'zhongwen'
					ul = 1234567L
					for result in results_list:
						i = 0
						for item in result:
							if type(item) == type(a):
								try:
									result[i] = item.encode('gb18030')
								except Exception, e:
									result[i] = item.replace(u'\xa0', u' ').encode('gb18030')
							elif type(item) == type(ul):
								try:
									result[i] = str(item) + "\t"
								except Exception, e:
									pass
							i = i + 1
					response = StreamingHttpResponse((writer.writerow(row) for row in results_list),
					                                 content_type="text/csv")
					response['Content-Disposition'] = 'attachment; filename="export.csv"'
					return response
				elif request.POST.has_key('query'):
					# check if table in black list and if user has permit to query
					# inBlackList,blacktb = bc.Sqlparse(a).check_query_table(choosed_host,request.user.username)
					# inBlackList, blacktb = func.mysql_blacklist_tb(a, request.user.username, choosed_host)
					# if inBlackList:
					# 	return render(request, 'oracle_query.html', locals())
					# get nomal query
					a, numlimit = oracle_fun.check_oracle_query(a, request.user.username)
					(data_list, collist, dbname) = oracle_fun.get_oracle_data(choosed_host, a, request.user.username,
					                                                          request,
					                                                          numlimit)
					# donot show wrong message sql
					if a == oracle_fun.wrong_msg:
						del a
					# print choosed_host
					return render(request, 'oracle_query.html', locals())
				# elif request.POST.has_key('sqladvice'):
				#
				# 	advice = func.get_advice(choosed_host, a, request)
				# 	return render(request, 'oracle_query.html', locals())

				return render(request, 'oracle_query.html', locals())

			except Exception, e:
				print e
				return render(request, 'oracle_query.html', locals())
		# return render(request, 'oracle_query.html', {'form':form,'choosed_host':choosed_host,'objlist':objlist})
		else:
			return render(request, 'oracle_query.html',
			              {'form': form, 'choosed_host': choosed_host, 'objlist': objlist})
	# return render(request, 'oracle_query.html', {'form': form,'objlist':objlist})
	else:
		form = AddForm()
		#
		# try:
		#     favword = request.session['myfavword']
		# except Exception,e:
		#     pass

		return render(request, 'oracle_query.html', locals())


@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_see_oracle_menu_inception_dml', login_url='/')
def oracle_inception_dml(request):
	# objlist = func.get_mysql_hostlist(request.user.username, 'meta')
	# result = func.get_diff('mysql-lepus-test','mysql_replication','mysql-lepus','mysql_replication')
	# print result
	form = AddForm(request.POST)
	objlist = oracle_fun.get_oracle_hostlist(request.user.username)
	# objlist = func.get_mysql_hostlist(request.user.username, 'incept')
	if request.method == 'POST':
		choosed_host = request.POST['dbhost']
		sqlmemo = request.POST['sqlmemo'][0:100]
		db_type_record = func.get_dbtype_bydbtag(choosed_host)
		dbtype_flag = str(db_type_record[0][0])
		dbname_flag = str(db_type_record[0][1])
		if len(sqlmemo) == 0:
			form = AddForm(request.POST)
			status = "Please input the memo"
			return render(request, 'oracle_inception_dml.html',
			              {"form": form, "objlist": objlist, 'choosed_host': choosed_host, "sqlmemo_val": sqlmemo,
			               "status": status})
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

				# data_mysql, collist, dbname = incept.inception_check(choosed_host, a, 2)
				data_mysql = ((1L, a, 0L),)
				collist = ['ID', 'sql_statement', 'ddlflag']
				dbname = dbname_flag
				# check the nee to split sqltext first

				if len(data_mysql) > 1:
					split = 1
					return render(request, 'oracle_inception_dml.html',
					              {"form": form, "objlist": objlist, "data_list": data_mysql, "collist": collist,
					               "split": split, 'choosed_host': choosed_host, "sqlmemo_val": sqlmemo})
				else:
					data_mysql, collist, dbname = incept.oracle_sqlcheck(a, dbname_flag)
				# data_mysql, collist, dbname = incept.inception_check(choosed_host, a)
				return render(request, 'oracle_inception_dml.html',
				              {"form": form, "objlist": objlist, "data_list": data_mysql, "collist": collist,
				               'choosed_host': choosed_host, "sqlmemo_val": sqlmemo})
			else:
				return render(request, 'oracle_inception_dml.html', locals())
		elif request.POST.has_key('addsql'):
			needbackup = 1
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
				# data_mysql, tmp_col, dbname = incept.inception_check(choosed_host, sqltext, 2)
				data_mysql = ((1L, sqltext, 0L),)
				collist = ['ID', 'sql_statement', 'ddlflag']
				dbname = dbname_flag
				# check if the sqltext need to be splited before uploaded
				if len(data_mysql) > 1:
					split = 1
					status = 'UPLOAD  FAIL'
					return render(request, 'oracle_inception_dml.html', {'form': form,
					                                                     'objlist': objlist,
					                                                     'status': status,
					                                                     'split': split,
					                                                     'choosed_host': choosed_host,
					                                                     "sqlmemo_val": sqlmemo})
				# check sqltext before uploaded
				else:
					tmp_data, tmp_col, tmp_col = incept.oracle_sqlcheck(sqltext, dbname_flag)
					# tmp_data, tmp_col, dbname = incept.inception_check(choosed_host, sqltext)
					for i in tmp_data:
						if int(i[2]) != 0:
							status = 'UPLOAD TASK FAIL,CHECK NOT PASSED'
							return render(request, 'oracle_inception_dml.html', locals())
				specification = "noaudit:" + sqlmemo;
				rstatus = 'check passed'
				myNewTask = incept.record_taskdml(request, sqltext, choosed_host, specification, needbackup, rstatus)
				nllflag = task_run(myNewTask.id, request)
				status = 'EXEC OK'
				datalist = Task.objects.filter(id=myNewTask.id).order_by("-create_time")[0:50]
				# sendmail_task.delay(choosed_host+'\n'+sqltext)
				# sendmail_task.delay(myNewTask)

				return render(request, 'oracle_inception_dml.html', {'form': form,
				                                                     'objlist': objlist,
				                                                     'status': status,
				                                                     'choosed_host': choosed_host, "datalist": datalist,
				                                                     "sqlmemo_val": sqlmemo})
			else:
				status = 'EXEC  FAIL'
				return render(request, 'oracle_inception_dml.html', {'form': form,
				                                                     'objlist': objlist,
				                                                     'status': status,
				                                                     'choosed_host': choosed_host,
				                                                     "sqlmemo_val": sqlmemo})
			form = AddForm()
			return render(request, 'oracle_inception_dml.html', {'form': form,
			                                                     'upform': upform,
			                                                     'objlist': objlist,
			                                                     'choosed_host': choosed_host, "sqlmemo_val": sqlmemo})
			return render(request, 'oracle_inception_dml.html', locals())
		# elif request.POST.has_key('addsql'):
		#     needbackup =1
		#     if form.is_valid():
		#         sqltext = form.cleaned_data['a']
		#         # get valid statement
		#         try:
		#             tmpsqltext = ''
		#             for i in sqlfilter.get_sqldml_detail(sqlfilter.sql_init_filter(sqltext), 2):
		#                 tmpsqltext = tmpsqltext + i
		#             sqltext = tmpsqltext
		#             form = AddForm(initial={'a': sqltext})
		#         except Exception, e:
		#             pass
		#         data_mysql, tmp_col, dbname = incept.inception_check(choosed_host, sqltext, 2)
		#         # check if the sqltext need to be splited before uploaded
		#         if len(data_mysql) > 1:
		#             split = 1
		#             status = 'UPLOAD  FAIL'
		#             return render(request, 'oracle_inception_dml.html', {'form': form,
		#                                                       'objlist': objlist,
		#                                                       'status': status,
		#                                                       'split': split,
		#                                                       'choosed_host': choosed_host,"sqlmemo_val":sqlmemo})
		#         # check sqltext before uploaded
		#         else:
		#             tmp_data, tmp_col, dbname = incept.inception_check(choosed_host, sqltext)
		#             for i in tmp_data:
		#                 if int(i[2]) != 0:
		#                     status = 'UPLOAD TASK FAIL,CHECK NOT PASSED'
		#                     return render(request, 'oracle_inception_dml.html', locals())
		#         specification="noaudit:"+sqlmemo;
		#         rstatus = 'check passed'
		#         myNewTask = incept.record_taskdml(request, sqltext, choosed_host, specification, needbackup,rstatus)
		#         nllflag = task_run(myNewTask.id, request)
		#         status = 'EXEC OK'
		#         datalist= Task.objects.filter(id=myNewTask.id).order_by("-create_time")[0:50]
		#         # sendmail_task.delay(choosed_host+'\n'+sqltext)
		#         #sendmail_task.delay(myNewTask)
		#
		#         return render(request, 'oracle_inception_dml.html', {'form': form,
		#                                                   'objlist': objlist,
		#                                                   'status': status,
		#                                                   'choosed_host': choosed_host,"datalist":datalist,"sqlmemo_val":sqlmemo})
		#     else:
		#         status = 'EXEC  FAIL'
		#         return render(request, 'oracle_inception_dml.html', {'form': form,
		#                                                   'objlist': objlist,
		#                                                   'status': status,
		#                                                   'choosed_host': choosed_host,"sqlmemo_val":sqlmemo})
		#     form = AddForm()
		#     return render(request, 'oracle_inception_dml.html', {'form': form,
		#                                           'upform': upform,
		#                                           'objlist': objlist,
		#                                           'choosed_host': choosed_host,"sqlmemo_val":sqlmemo})
		#     return render(request, 'oracle_inception_dml.html', locals())
		else:
			return render(request, 'oracle_inception_dml.html', locals())

	elif request.method == 'GET':
		return render(request, 'oracle_inception_dml.html', locals())
	else:
		return render(request, 'oracle_inception_dml.html', locals())


@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_see_oracle_menu_inception_ddldml', login_url='/')
def oracle_inception_ddldml(request):
	# objlist = func.get_mysql_hostlist(request.user.username,'incept')
	objlist = oracle_fun.get_oracle_hostlist(request.user.username)
	if request.method == 'POST':
		if request.POST.has_key('searchdb'):
			db_se = request.POST['searchdbname']
			# objlist_tmp = func.get_mysql_hostlist(request.user.username, 'incept', db_se)
			objlist_tmp = oracle_fun.get_oracle_hostlist(request.user.username, 'incept', db_se)
			# incase not found any db
			if len(objlist_tmp) > 0:
				objlist = objlist_tmp
		choosed_host = request.POST['cx']
		specification = request.POST['specification'][0:100]
		db_type_record = func.get_dbtype_bydbtag(choosed_host)
		dbtype_flag = str(db_type_record[0][0])
		dbname_flag = str(db_type_record[0][1])
		if not User.objects.get(username=request.user.username).db_name_set.filter(dbtag=choosed_host)[:1]:
			return HttpResponseRedirect("/")
		if request.POST.has_key('check'):
			form = AddForm(request.POST)
			if form.is_valid():
				a = form.cleaned_data['a']

				# choosed_host = request.POST['cx']
				# get valid statement
				try:
					tmpsqltext = ''
					for i in sqlfilter.get_oracle_sql_detail(sqlfilter.sql_init_filter(a), 2):
						tmpsqltext = tmpsqltext + i
					a = tmpsqltext
					form = AddForm(initial={'a': a})
				except Exception, e:
					pass

				# data_mysql, collist, dbname = incept.inception_check(choosed_host,a,2)
				data_mysql = ((1L, a, 0L),)
				collist = ['ID', 'sql_statement', 'ddlflag']
				dbname = dbname_flag
				# check the nee to split sqltext first
				if len(data_mysql) > 1:
					split = 1
					return render(request, 'oracle_inception_ddldml.html', {'form': form,

					                                                        'objlist': objlist,
					                                                        'data_list': data_mysql,
					                                                        'collist': collist,
					                                                        'choosed_host': choosed_host,
					                                                        'specification_val': specification,
					                                                        'split': split})
				else:
					# data_mysql,collist,dbname = incept.inception_check(choosed_host,a)
					data_mysql, collist, dbname = incept.oracle_sqlcheck(a, dbname_flag)
					return render(request, 'oracle_inception_ddldml.html', {'form': form,
					                                                        'objlist': objlist,
					                                                        'data_list': data_mysql,
					                                                        'collist': collist,
					                                                        'specification_val': specification,
					                                                        'choosed_host': choosed_host})
			else:
				# print "not valid"
				return render(request, 'oracle_inception_ddldml.html', {'form': form,
				                                                        'specification_val': specification,
				                                                        'objlist': objlist})
		elif request.POST.has_key('addtask'):
			form = AddForm(request.POST)
			needbackup = (int(request.POST['ifbackup']) if int(request.POST['ifbackup']) in (0, 1) else 1)

			# choosed_host = request.POST['cx']
			if form.is_valid():
				sqltext = form.cleaned_data['a']
				# get valid statement
				try:
					tmpsqltext = ''
					#for i in sqlfilter.get_oracle_sqldml_detail(sqlfilter.sql_init_filter(sqltext), 2):
					for i in sqlfilter.get_oracle_sql_detail(sqlfilter.sql_init_filter(sqltext), 2):
						tmpsqltext = tmpsqltext + i
					sqltext = tmpsqltext
					form = AddForm(initial={'a': sqltext})
				except Exception, e:
					pass
				# data_mysql, tmp_col, dbname = incept.inception_check(choosed_host, sqltext, 2)
				data_mysql = ((1L, sqltext, 0L),)
				collist = ['ID', 'sql_statement', 'ddlflag']
				dbname = dbname_flag
				# check if the sqltext need to be splited before uploaded
				if len(data_mysql) > 1:
					split = 1
					status = 'UPLOAD TASK FAIL'
					return render(request, 'oracle_inception_ddldml.html', {'form': form,
					                                                        'objlist': objlist,
					                                                        'status': status,
					                                                        'split': split,
					                                                        'specification_val': specification,
					                                                        'choosed_host': choosed_host})
				# check sqltext before uploaded
				else:
					# tmp_data, tmp_col, dbname = incept.inception_check(choosed_host, sqltext)
					tmp_data, tmp_col, dbname = incept.oracle_sqlcheck(sqltext, dbname_flag)
					for i in tmp_data:
						if int(i[2]) != 0:
							status = 'UPLOAD TASK FAIL,CHECK NOT PASSED'
							return render(request, 'oracle_inception_ddldml.html', locals())
				myNewTask = incept.record_task(request, sqltext, choosed_host, specification, needbackup)
				status = 'UPLOAD TASK OK'
				# sendmail_task.delay(choosed_host+'\n'+sqltext)
				# sendmail_task.delay(myNewTask)

				return render(request, 'oracle_inception_ddldml.html', {'form': form,
				                                                        'objlist': objlist,
				                                                        'specification_val': specification,
				                                                        'status': status,
				                                                        'choosed_host': choosed_host})
			else:
				status = 'UPLOAD TASK FAIL'
				return render(request, 'oracle_inception_ddldml.html', {'form': form,
				                                                        'objlist': objlist,
				                                                        'specification_val': specification,
				                                                        'status': status,
				                                                        'choosed_host': choosed_host})
		form = AddForm()
		return render(request, 'oracle_inception_ddldml.html', {'form': form,
		                                                        'objlist': objlist,
		                                                        'specification_val': specification,
		                                                        'choosed_host': choosed_host})
	else:
		form = AddForm()
		return render(request, 'oracle_inception_ddldml.html', {'form': form,
		                                                        'objlist': objlist})


@login_required(login_url='/accounts/login/')
@permission_required('myapp.can_see_oracle_menu_oracle_exec', login_url='/')
def oracle_exec(request):
	try:
		favword = request.COOKIES['myfavword']
	except Exception, e:
		pass
	# print request.user.username
	objlist = oracle_fun.get_oracle_hostlist(request.user.username, 'exec')
	if request.method == 'POST':
		form = AddForm(request.POST)
		choosed_host = request.POST['cx']
		db_type_record = func.get_dbtype_bydbtag(choosed_host)
		dbtype_flag = str(db_type_record[0][0])
		dbname_flag = str(db_type_record[0][1])
		if not User.objects.get(username=request.user.username).db_name_set.filter(dbtag=choosed_host)[:1]:
			return HttpResponseRedirect("/")
		if request.POST.has_key('searchdb'):
			db_se = request.POST['searchdbname']
			objlist_tmp = oracle_fun.get_oracle_hostlist(request.user.username, 'exec', db_se)
			# incase not found any db
			if len(objlist_tmp) > 0:
				objlist = objlist_tmp

		if form.is_valid():
			a = form.cleaned_data['a']
			# try to get the first valid sql
			try:
				#a = sqlfilter.get_oracle_sql_detail(sqlfilter.sql_init_filter(a), 2)
				tmpsqltext = ''
				# for i in sqlfilter.get_oracle_sqldml_detail(sqlfilter.sql_init_filter(sqltext), 2):
				for i in sqlfilter.get_oracle_sql_detail(sqlfilter.sql_init_filter(a), 2):
					tmpsqltext = tmpsqltext + i
				sqltext = tmpsqltext
				form = AddForm(initial={'a': sqltext})
				# form = AddForm(initial={'a': a})
			except Exception, e:
				a = 'wrong'
			sql = sqltext
			a = oracle_fun.check_oracle_exec(sqltext, request)
			# print request.POST
			if request.POST.has_key('commit'):
				(data_mysql, collist, dbname) = oracle_fun.run_orcle_exec(choosed_host, a, request.user.username,
				                                                          request)
			elif request.POST.has_key('check'):
				# data_mysql,collist,dbname = incept.inception_check(choosed_host,a)
				data_mysql, collist, dbname = incept.oracle_sqlcheck(a, dbname_flag)
			# return render(request,'mysql_exec.html',{'form': form,'objlist':objlist,'data_mysql':data_mysql,'collist':collist,'choosed_host':choosed_host,'dbname':dbname})

			return render(request, 'mysql_exec.html', locals())
		else:
			return render(request, 'mysql_exec.html', locals())

			# return render(request, 'mysql_exec.html', {'form': form,'objlist':objlist})
	else:
		form = AddForm()
		return render(request, 'mysql_exec.html', locals())

		# return render(request, 'mysql_exec.html', {'form': form,'objlist':objlist})
