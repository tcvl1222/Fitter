# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-05-27 09:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fitterKakao', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='question',
        ),
        migrations.AddField(
            model_name='person',
            name='shoulder_a',
            field=models.IntegerField(default=1),
        ),
    ]