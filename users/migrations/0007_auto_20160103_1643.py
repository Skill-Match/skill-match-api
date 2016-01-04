# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-04 00:43
from __future__ import unicode_literals

import cloudinary.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20160103_1631'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='pic_url',
            field=models.URLField(default='http://res.cloudinary.com/skill-match/image/upload/c_scale,w_200/v1451856958/Man_cqggt4.png', max_length=300),
        ),
        migrations.AddField(
            model_name='profile',
            name='small_pic_url',
            field=models.URLField(default='http://res.cloudinary.com/skill-match/image/upload/c_scale,w_50/v1451856958/Man_cqggt4.png', max_length=300),
        ),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=cloudinary.models.CloudinaryField(blank=True, max_length=255, null=True, verbose_name='image'),
        ),
    ]