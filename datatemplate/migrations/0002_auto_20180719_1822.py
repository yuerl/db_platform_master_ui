# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('datatemplate', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='template_mgr',
            old_name='sql_memo',
            new_name='templtememo',
        ),
        migrations.RenameField(
            model_name='template_mgr',
            old_name='status',
            new_name='templtestatus',
        ),
        migrations.RemoveField(
            model_name='template_mgr',
            name='add_task',
        ),
        migrations.RemoveField(
            model_name='template_mgr',
            name='dbtag',
        ),
        migrations.RemoveField(
            model_name='template_mgr',
            name='operator',
        ),
        migrations.RemoveField(
            model_name='template_mgr',
            name='sche_time',
        ),
        migrations.AddField(
            model_name='template_mgr',
            name='templtename',
            field=models.CharField(default=datetime.datetime(2018, 7, 19, 10, 22, 13, 406747, tzinfo=utc), max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='template_mgr',
            name='templteno',
            field=models.CharField(default='x', max_length=50),
            preserve_default=False,
        ),
    ]
