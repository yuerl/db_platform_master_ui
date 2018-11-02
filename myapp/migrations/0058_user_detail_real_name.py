# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0057_auto_20180927_1023'),
    ]

    operations = [
        migrations.AddField(
            model_name='user_detail',
            name='real_name',
            field=models.CharField(default='', max_length=35),
            preserve_default=False,
        ),
    ]
