# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20151021_0540'),
    ]

    operations = [
        migrations.RenameField(
            model_name='page',
            old_name='update_date',
            new_name='last_update',
        ),
        migrations.AddField(
            model_name='classroom',
            name='first_date',
            field=models.DateField(null=True, editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='classroom',
            name='instructor',
            field=models.CharField(default='', max_length=256, editable=False, blank=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='page',
            name='print_format',
            field=models.CharField(default='print_page.tex', max_length=256, editable=False, choices=[('print_page.tex', 'Page'), ('print_book.tex', 'Book'), ('print_equipment_form.tex', 'Equipment')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='access_level',
            field=models.PositiveSmallIntegerField(default=0, editable=False, choices=[(0, 'Public'), (1, 'Student'), (2, 'Instructor')]),
            preserve_default=True,
        ),
    ]
