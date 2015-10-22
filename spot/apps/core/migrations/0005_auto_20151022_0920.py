# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20151022_0823'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='print_format',
            field=models.CharField(default='print_page.tex', max_length=256, editable=False, choices=[('print_page.tex', 'Page'), ('print_book.tex', 'Book'), ('print_exam.tex', 'Exam'), ('print_form.tex', 'Equipment')]),
            preserve_default=True,
        ),
    ]
