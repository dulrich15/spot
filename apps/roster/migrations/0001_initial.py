# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_student'),
    ]

    operations = [
        migrations.CreateModel(
            name='Assignment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200, null=True, blank=True)),
                ('due_date', models.DateField(null=True, blank=True)),
                ('max_points', models.PositiveSmallIntegerField(default=0)),
                ('curve_points', models.PositiveSmallIntegerField(default=0)),
                ('is_graded', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['category', 'due_date'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AssignmentCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=200)),
                ('weight_raw', models.PositiveSmallIntegerField(default=1)),
            ],
            options={
                'ordering': ['scheme', '-weight_raw', 'name'],
                'verbose_name_plural': 'assignment categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AssignmentGrade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('earned_points', models.PositiveSmallIntegerField(default=0)),
                ('extra_points', models.PositiveSmallIntegerField(default=0)),
                ('is_excused', models.BooleanField(default=False)),
                ('assignment', models.ForeignKey(to='roster.Assignment')),
                ('student', models.ForeignKey(to='core.Student')),
            ],
            options={
                'ordering': ['assignment__category', 'assignment'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GradeScheme',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('classroom', models.OneToOneField(to='core.Classroom')),
            ],
            options={
                'ordering': ['classroom'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='assignmentcategory',
            name='scheme',
            field=models.ForeignKey(to='roster.GradeScheme'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assignment',
            name='category',
            field=models.ForeignKey(to='roster.AssignmentCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='assignment',
            name='classroom',
            field=models.ForeignKey(to='core.Classroom'),
            preserve_default=True,
        ),
    ]
