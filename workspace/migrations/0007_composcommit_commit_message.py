# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-19 11:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspace', '0006_auto_20171017_0026'),
    ]

    operations = [
        migrations.AddField(
            model_name='composcommit',
            name='commit_message',
            field=models.CharField(default='commit message', max_length=128),
        ),
    ]