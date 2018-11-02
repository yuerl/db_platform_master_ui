# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0045_mysql_check_mysql_hosts'),
    ]

    operations = [
        migrations.RenameField(
            model_name='mysql_check',
            old_name='status',
            new_name='chk_status',
        ),
        migrations.RenameField(
            model_name='mysql_check',
            old_name='hosts',
            new_name='chk_type',
        ),
        migrations.RenameField(
            model_name='mysql_check',
            old_name='type',
            new_name='hosts_ip',
        ),
        migrations.RenameField(
            model_name='mysql_hosts',
            old_name='hosts',
            new_name='hosts_ip',
        ),
    ]
