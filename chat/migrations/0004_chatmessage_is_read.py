# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-20 12:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_auto_20171119_1841'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='is_read',
            field=models.BooleanField(default=False),
        ),
    ]
