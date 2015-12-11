# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-11 19:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchup', '0017_auto_20151211_1104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='feedback',
            name='punctuality',
            field=models.CharField(choices=[('No Show', 'No Show'), ('On Time', 'On Time'), ('Little bit late', 'Little bit late'), ('Late', 'Over 10 min late')], default='On Time', max_length=15, null=True),
        ),
    ]