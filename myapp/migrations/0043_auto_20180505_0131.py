# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0042_pro_mgr_detail_sql_memo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pro_mgr_detail',
            name='pro_id',
            field=models.ForeignKey(to='myapp.Pro_mgr'),
        ),
    ]
