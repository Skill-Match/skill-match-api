# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-02 23:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchup', '0004_auto_20160102_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hendersonpark',
            name='img_url',
            field=models.URLField(blank=True, max_length=350, null=True),
        ),
        migrations.AlterField(
            model_name='hendersonpark',
            name='name',
            field=models.CharField(max_length=200),
        ),
    ]
