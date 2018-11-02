# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0046_auto_20180512_0111'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysql_hosts',
            name='host_pwd',
            field=models.CharField(default='', max_length=100),
        ),
        migrations.AddField(
            model_name='mysql_hosts',
            name='host_user',
            field=models.CharField(default='', max_length=50),
        ),
        migrations.AlterField(
            model_name='mysql_hosts',
            name='host_status',
            field=models.CharField(default='', max_length=20),
        ),
    ]
