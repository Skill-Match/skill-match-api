# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-03 04:18
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matchup', '0007_hendersonpark_park'),
    ]

    operations = [
        migrations.AddField(
            model_name='court',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
    ]