# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-20 15:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspace', '0010_auto_20171218_1659'),
    ]

    operations = [
        migrations.AddField(
            model_name='compos',
            name='is_public',
            field=models.BooleanField(default=False),
        ),
    ]
