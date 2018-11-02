# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0056_auto_20180927_0919'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user_detail',
            old_name='department',
            new_name='position',
        ),
    ]
