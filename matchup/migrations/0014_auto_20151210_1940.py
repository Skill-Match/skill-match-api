# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-11 03:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchup', '0013_park_yelp_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='park',
            name='yelp_id',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]