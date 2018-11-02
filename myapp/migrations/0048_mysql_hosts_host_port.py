# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0047_auto_20180512_0157'),
    ]

    operations = [
        migrations.AddField(
            model_name='mysql_hosts',
            name='host_port',
            field=models.IntegerField(default=3306),
        ),
    ]
