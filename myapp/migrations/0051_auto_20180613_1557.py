# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0050_mysql_dbcompare_mysql_initdata'),
    ]

    operations = [
        migrations.AddField(
            model_name='pro_mgr',
            name='memo',
            field=models.CharField(default='', max_length=300),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='pro_mgr_detail',
            name='sql_memo',
            field=models.CharField(default='', max_length=50),
        ),
    ]
