# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-01-25 05:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notepad', '0008_note_archiving'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='history',
            field=models.IntegerField(null=True),
        ),
    ]
