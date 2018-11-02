# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0044_pro_mgr_detail_add_task'),
    ]

    operations = [
        migrations.CreateModel(
            name='mysql_check',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hosts', models.CharField(max_length=35)),
                ('type', models.CharField(max_length=35)),
                ('status', models.CharField(max_length=20)),
                ('msg', models.CharField(max_length=500)),
                ('dtime', models.DateTimeField(db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='mysql_hosts',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hosts', models.CharField(max_length=35)),
                ('host_status', models.CharField(max_length=20)),
                ('dtime', models.DateTimeField(db_index=True)),
            ],
        ),
    ]
