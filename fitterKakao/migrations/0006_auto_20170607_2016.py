# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-07 11:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fitterKakao', '0005_auto_20170607_2002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='name',
            field=models.CharField(max_length=10),
        ),
    ]