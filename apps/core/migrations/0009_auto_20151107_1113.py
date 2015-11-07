# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20151101_0038'),
    ]

    operations = [
        migrations.AddField(
            model_name='classroom',
            name='is_active',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='page',
            name='print_template',
            field=models.CharField(default='print_page.tex', max_length=256, editable=False, choices=[('print_page.tex', 'Page'), ('print_book.tex', 'Book'), ('print_book2.tex', 'Book2'), ('print_exam.tex', 'Exam'), ('print_equipment_form.tex', 'Equipment')]),
            preserve_default=True,
        ),
    ]
