# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-03 05:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matchup', '0008_court_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='court',
            name='park',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='matchup.Park'),
        ),
    ]