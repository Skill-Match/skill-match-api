# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-15 01:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchup', '0020_auto_20151214_1709'),
    ]

    operations = [
        migrations.AddField(
            model_name='skill',
            name='num_feedbacks',
            field=models.IntegerField(null=True),
        ),
    ]
