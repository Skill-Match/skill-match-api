# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-03 21:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20160103_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='pic_url',
            field=models.URLField(default='http://res.cloudinary.com/skill-match/image/upload/c_scale,w_200/v1451856958/Man_cqggt4.png', max_length=300),
        ),
    ]