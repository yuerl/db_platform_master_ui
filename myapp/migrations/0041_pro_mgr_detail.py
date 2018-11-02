# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0040_auto_20180430_0021'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pro_mgr_detail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('user', models.CharField(max_length=35)),
                ('dbtag', models.CharField(max_length=35)),
                ('pro_id', models.CharField(max_length=35)),
                ('sqltext', models.TextField()),
                ('create_time', models.DateTimeField(db_index=True)),
                ('update_time', models.DateTimeField()),
                ('status', models.CharField(max_length=20, db_index=True)),
                ('sqlsha', models.TextField()),
                ('sche_time', models.DateTimeField(default='2199-01-01 00:00:00', db_index=True)),
                ('operator', models.CharField(default='', max_length=35)),
            ],
        ),
    ]
