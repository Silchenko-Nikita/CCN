# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-11-20 15:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_userprofile_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='about_me',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
