# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0051_auto_20180613_1557'),
    ]

    operations = [
        migrations.CreateModel(
            name='mysql_check_command',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hosts_ip', models.CharField(max_length=35)),
                ('command', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('count', models.IntegerField()),
                ('dtime', models.DateTimeField(db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='mysql_check_space',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hosts_ip', models.CharField(max_length=35)),
                ('table_schema', models.CharField(max_length=50)),
                ('table_name', models.CharField(max_length=50)),
                ('table_rows', models.IntegerField()),
                ('data_length', models.IntegerField()),
                ('dtime', models.DateTimeField(db_index=True)),
            ],
        ),
    ]
