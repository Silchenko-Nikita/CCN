# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-10-16 21:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspace', '0005_auto_20171016_2108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='composcommit',
            name='title',
            field=models.CharField(default='blabla', max_length=512),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='compos',
            name='title',
            field=models.CharField(default='blabla', max_length=512),
            preserve_default=False,
        ),
    ]
