# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0054_auto_20180808_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='pro_mgr',
            name='stage',
            field=models.CharField(default='dev', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pro_mgr',
            name='stage_time',
            field=models.DateTimeField(default='2018-08-28 12:00:00', db_index=True),
            preserve_default=False,
        ),
    ]
