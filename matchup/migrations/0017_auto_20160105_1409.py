# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-05 22:09
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matchup', '0016_auto_20160104_2129'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='park',
            name='mobile_url',
        ),
        migrations.RemoveField(
            model_name='park',
            name='yelp_id',
        ),
    ]
