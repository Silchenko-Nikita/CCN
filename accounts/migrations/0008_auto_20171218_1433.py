# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-18 12:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_userprofile_friends'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='friends',
            field=models.ManyToManyField(related_name='_userprofile_friends_+', to='accounts.UserProfile'),
        ),
    ]
