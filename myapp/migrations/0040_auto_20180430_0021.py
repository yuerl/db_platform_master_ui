# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0039_auto_20170424_1537'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pro_mgr',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('prono', models.CharField(max_length=50)),
                ('proname', models.CharField(max_length=50)),
                ('user', models.CharField(max_length=35)),
                ('mgr_user', models.CharField(max_length=35)),
                ('status', models.CharField(max_length=30)),
                ('create_time', models.DateTimeField(db_index=True)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='pro_mgr',
            unique_together=set([('proname', 'mgr_user')]),
        ),
    ]
