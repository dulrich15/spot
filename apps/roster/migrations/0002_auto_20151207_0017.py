# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0011_auto_20151207_0017'),
        ('roster', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('classroom', models.ForeignKey(to='core.Classroom')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['user__last_name', 'user__first_name'],
            },
            bases=(models.Model,),
        ),
        migrations.AlterField(
            model_name='assignmentgrade',
            name='student',
            field=models.ForeignKey(to='roster.Student'),
            preserve_default=True,
        ),
    ]
