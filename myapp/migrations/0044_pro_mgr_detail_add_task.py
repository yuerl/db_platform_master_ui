# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0043_auto_20180505_0131'),
    ]

    operations = [
        migrations.AddField(
            model_name='pro_mgr_detail',
            name='add_task',
            field=models.CharField(default='no', max_length=10),
        ),
    ]
