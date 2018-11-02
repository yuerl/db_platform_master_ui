# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='template_mgr',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_user', models.CharField(max_length=35)),
                ('dbtag', models.CharField(max_length=35)),
                ('sqltext', models.TextField()),
                ('sql_memo', models.CharField(default=b'', max_length=200)),
                ('create_time', models.DateTimeField(db_index=True)),
                ('update_time', models.DateTimeField()),
                ('status', models.CharField(max_length=20, db_index=True)),
                ('sche_time', models.DateTimeField(default=b'2199-01-01 00:00:00', db_index=True)),
                ('operator', models.CharField(default=b'', max_length=35)),
                ('add_task', models.CharField(default=b'no', max_length=10)),
            ],
        ),
    ]
