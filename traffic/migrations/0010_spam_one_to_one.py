# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-01-24 05:41
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('traffic', '0009_change_spam_overflow'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spam',
            name='visit',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, to='traffic.Visit'),
        ),
    ]
