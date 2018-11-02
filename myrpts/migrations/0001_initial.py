# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='rpt_sql',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sqlno', models.CharField(max_length=50)),
                ('sqltext', models.TextField()),
                ('sqlmemo', models.CharField(max_length=50)),
                ('status', models.CharField(max_length=30)),
                ('create_time', models.DateTimeField(db_index=True)),
                ('update_time', models.DateTimeField(db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='rpt_sql_detail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('detail_no', models.CharField(max_length=100)),
                ('param_stype', models.CharField(max_length=50)),
                ('param_value', models.CharField(max_length=100)),
                ('param_status', models.CharField(max_length=50)),
                ('create_time', models.DateTimeField(db_index=True)),
                ('update_time', models.DateTimeField(db_index=True)),
                ('sql_id', models.ForeignKey(to='myrpts.rpt_sql')),
            ],
        ),
    ]
