# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-02 09:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(blank=True, default=None, max_length=512, null=True)),
                ('users', models.ManyToManyField(related_name='chats', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Chats',
                'db_table': 'chat',
                'verbose_name': 'Chat',
            },
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('text', models.TextField()),
                ('author', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('chat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.Chat')),
            ],
            options={
                'verbose_name_plural': 'Chat messages',
                'db_table': 'chat_message',
                'verbose_name': 'Chat message',
            },
        ),
    ]
