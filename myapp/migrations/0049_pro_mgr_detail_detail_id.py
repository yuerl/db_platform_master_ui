# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0048_mysql_hosts_host_port'),
    ]

    operations = [
        migrations.AddField(
            model_name='pro_mgr_detail',
            name='detail_id',
            field=models.IntegerField(default=0),
        ),
    ]
