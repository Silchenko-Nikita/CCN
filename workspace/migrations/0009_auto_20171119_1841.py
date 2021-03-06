# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-19 16:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workspace', '0008_auto_20171119_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='compos',
            name='status',
            field=models.IntegerField(choices=[(1, 'Active'), (2, 'Deleted')], default=1),
        ),
        migrations.AddField(
            model_name='composbranch',
            name='status',
            field=models.IntegerField(choices=[(1, 'Active'), (2, 'Deleted')], default=1),
        ),
        migrations.AddField(
            model_name='composcommit',
            name='status',
            field=models.IntegerField(choices=[(1, 'Active'), (2, 'Deleted')], default=1),
        ),
    ]
