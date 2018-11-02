from django.db import models
import django.utils.timezone as timezone
class rpt_sql(models.Model):
    sqlno=models.CharField(max_length=50)
    sqltext=models.TextField()
    sqlmemo = models.CharField(max_length=50)
    status=models.CharField(max_length=30)
    create_time = models.DateTimeField(db_index=True)
    update_time = models.DateTimeField(db_index=True)
#setting where
class rpt_sql_detail(models.Model):
    detail_no=models.CharField(max_length=100)
    sql_id=models.ForeignKey(to="rpt_sql", to_field="id")
    param_stype = models.CharField(max_length=50)
    param_value= models.CharField(max_length=100)
    param_status=models.CharField(max_length=50)
    create_time = models.DateTimeField(db_index=True)
    update_time = models.DateTimeField(db_index=True)