# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-17 00:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchup', '0024_court'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='is_challenge',
            field=models.NullBooleanField(default=False),
        ),
    ]
