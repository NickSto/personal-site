# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-20 21:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('notepad', '0006_move_visit_fix'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='visit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='traffic.Visit'),
        ),
    ]