# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-05 00:32
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matchup', '0014_auto_20160103_2009'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='feedback',
            name='court_ranking',
        ),
    ]