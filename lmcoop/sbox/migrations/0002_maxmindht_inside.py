# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-12-26 07:17
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sbox', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='maxmindht',
            name='inside',
            field=models.BooleanField(default=True),
        ),
    ]