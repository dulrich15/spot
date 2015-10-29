# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_auto_20151022_0920'),
    ]

    operations = [
        migrations.RenameField(
            model_name='page',
            old_name='print_format',
            new_name='print_template',
        ),
    ]
