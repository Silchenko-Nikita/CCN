# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-18 12:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20171120_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='friends',
            field=models.ManyToManyField(to='accounts.UserProfile'),
        ),
    ]