# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_page_print_format'),
    ]

    operations = [
        migrations.RenameField(
            model_name='page',
            old_name='update_date',
            new_name='last_update',
        ),
    ]
