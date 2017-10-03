# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-10-03 06:08
from __future__ import unicode_literals

from django.db import migrations, models
import utils.misc


class Migration(migrations.Migration):

    dependencies = [
        ('traffic', '0003_visitor_version'),
    ]

    operations = [
        migrations.CreateModel(
            name='Robot',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(blank=True, null=True)),
                ('cookie1', models.CharField(blank=True, max_length=24, null=True)),
                ('cookie2', models.CharField(blank=True, max_length=24, null=True)),
                ('user_agent', models.CharField(blank=True, max_length=200, null=True)),
                ('version', models.SmallIntegerField()),
            ],
            bases=(utils.misc.ModelMixin, models.Model),
        ),
        migrations.AddField(
            model_name='visitor',
            name='bot_score',
            field=models.IntegerField(default=0),
        ),
    ]
