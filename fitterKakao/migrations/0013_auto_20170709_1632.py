# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-07-09 07:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fitterKakao', '0012_person_sex'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClothesNick',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nick', models.CharField(default='Untitled', max_length=20)),
            ],
        ),
        migrations.AlterField(
            model_name='topclothes',
            name='nick',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fitterKakao.ClothesNick'),
        ),
    ]
