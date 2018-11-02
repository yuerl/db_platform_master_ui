from django.db import models

# Create your models here.
class template_mgr(models.Model):
    templteno = models.CharField(max_length=50)
    templtename = models.CharField(max_length=100)
    templtestatus = models.CharField(max_length=20, db_index=True)
    templtememo = models.CharField(max_length=200, default='')
    create_user = models.CharField(max_length=35)
    create_time = models.DateTimeField(db_index=True)
    sqltext = models.TextField()
    update_time = models.DateTimeField()

    def __unicode__(self):
        return self.dbtag