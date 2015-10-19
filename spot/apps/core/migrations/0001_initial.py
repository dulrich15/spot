# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(unique=True, max_length=64)),
                ('is_active', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=256, editable=False, blank=True)),
                ('subtitle', models.CharField(max_length=256, editable=False, blank=True)),
            ],
            options={
                'ordering': ['slug'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('url', models.CharField(unique=True, max_length=1024)),
                ('access_level', models.PositiveSmallIntegerField(default=0, choices=[(0, 'Public'), (1, 'Student'), (2, 'Instructor')])),
                ('content', models.TextField(blank=True)),
                ('title', models.CharField(max_length=256, editable=False, blank=True)),
                ('subtitle', models.CharField(max_length=256, editable=False, blank=True)),
                ('author', models.CharField(max_length=256, editable=False, blank=True)),
                ('date', models.DateField(null=True, editable=False, blank=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('update_date', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(blank=True, editable=False, to='core.Page', null=True)),
            ],
            options={
                'ordering': ['url'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='classroom',
            name='home_page',
            field=models.ForeignKey(editable=False, to='core.Page'),
            preserve_default=True,
        ),
    ]
