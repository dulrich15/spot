# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20151022_1504'),
    ]

    operations = [
        migrations.RenameField(
            model_name='page',
            old_name='content',
            new_name='raw_content',
        ),
        migrations.AlterField(
            model_name='classroom',
            name='banner_filename',
            field=models.CharField(max_length=200, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='print_template',
            field=models.CharField(default='print_page.tex', max_length=256, editable=False, choices=[('print_page.tex', 'Page'), ('print_book.tex', 'Book'), ('print_exam.tex', 'Exam'), ('print_equipment_form.tex', 'Equipment')]),
            preserve_default=True,
        ),
    ]
