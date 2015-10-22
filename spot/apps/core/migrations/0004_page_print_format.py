# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20151021_0540'),
    ]

    operations = [
        migrations.AddField(
            model_name='page',
            name='print_format',
            field=models.CharField(default='page', max_length=256),
            preserve_default=True,
        ),
    ]
