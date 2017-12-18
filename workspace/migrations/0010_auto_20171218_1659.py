# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-18 14:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspace', '0009_auto_20171119_1841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='compos',
            name='compos_id',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='composbranch',
            name='branch_id',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='composcommit',
            name='commit_id',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
