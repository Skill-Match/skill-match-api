# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-06 19:42
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matchup', '0003_auto_20160106_1140'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hendersonpark',
            name='park',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='henderson_park', to='matchup.Park'),
        ),
    ]
