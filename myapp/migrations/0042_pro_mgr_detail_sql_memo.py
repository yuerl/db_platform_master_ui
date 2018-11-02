# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0041_pro_mgr_detail'),
    ]

    operations = [
        migrations.AddField(
            model_name='pro_mgr_detail',
            name='sql_memo',
            field=models.CharField(default=0, max_length=50),
            preserve_default=False,
        ),
    ]
