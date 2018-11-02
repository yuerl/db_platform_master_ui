# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0049_pro_mgr_detail_detail_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='mysql_dbcompare',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('row_number', models.IntegerField()),
                ('stype', models.CharField(max_length=30)),
                ('host0', models.CharField(max_length=50)),
                ('item0', models.CharField(max_length=100)),
                ('host1', models.CharField(max_length=50)),
                ('item1', models.CharField(max_length=100)),
                ('result', models.TextField()),
                ('dbtime', models.DateTimeField(db_index=True)),
            ],
        ),
        migrations.CreateModel(
            name='mysql_initdata',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dbtag', models.CharField(max_length=35)),
                ('init_table', models.CharField(max_length=100)),
                ('init_status', models.CharField(default='yes', max_length=50)),
                ('dtime', models.DateTimeField(db_index=True)),
            ],
        ),
    ]
