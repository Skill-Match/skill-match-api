# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-06 07:51
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ammenity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=125)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Court',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sport', models.CharField(choices=[('Tennis', 'Tennis'), ('Basketball', 'Basketball'), ('Football', 'Football'), ('Soccer', 'Soccer'), ('Volleyball', 'Volleyball'), ('Pickleball', 'Pickleball'), ('Other', 'Other')], max_length=25)),
                ('other', models.CharField(blank=True, max_length=25, null=True)),
                ('num_courts', models.IntegerField(blank=True, null=True)),
                ('img_url', models.URLField(default='http://res.cloudinary.com/skill-match/image/upload/v1451804013/trophy_200_cnaras.jpg')),
                ('location', django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('skill', models.PositiveIntegerField()),
                ('sportsmanship', models.PositiveIntegerField()),
                ('availability', models.PositiveIntegerField()),
                ('punctuality', models.CharField(choices=[('No Show', 'No Show'), ('On Time', 'On Time'), ('Little bit late', 'Little bit late'), ('Late', 'Over 10 min late')], default='On Time', max_length=15)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='HendersonPark',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('address', models.CharField(max_length=150)),
                ('url', models.URLField()),
                ('img_url', models.URLField(blank=True, max_length=350, null=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('modifided_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, max_length=1000, null=True)),
                ('sport', models.CharField(choices=[('Tennis', 'Tennis'), ('Basketball', 'Basketball'), ('Football', 'Football'), ('Soccer', 'Soccer'), ('Volleyball', 'Volleyball'), ('Pickleball', 'Pickleball'), ('Other', 'Other')], default='Tennis', max_length=25)),
                ('other', models.CharField(blank=True, max_length=25, null=True)),
                ('skill_level', models.PositiveIntegerField()),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('img_url', models.URLField(default='http://res.cloudinary.com/skill-match/image/upload/v1451804013/trophy_200_cnaras.jpg')),
                ('is_open', models.BooleanField(default=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('is_challenge', models.BooleanField(default=False)),
                ('challenge_declined', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True, null=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_matches', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Park',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.FloatField()),
                ('rating_img_url', models.URLField(max_length=300)),
                ('rating_img_url_small', models.URLField(max_length=300)),
                ('name', models.CharField(max_length=200)),
                ('url', models.URLField()),
                ('image_url', models.URLField(blank=True, null=True)),
                ('city', models.CharField(max_length=50)),
                ('display_address1', models.CharField(max_length=40)),
                ('display_address2', models.CharField(max_length=40)),
                ('display_address3', models.CharField(blank=True, max_length=40, null=True)),
                ('postal_code', models.CharField(max_length=10)),
                ('location', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('state_code', models.CharField(max_length=5)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.AddField(
            model_name='match',
            name='park',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matchup.Park'),
        ),
        migrations.AddField(
            model_name='match',
            name='players',
            field=models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='hendersonpark',
            name='park',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='matchup.Park'),
        ),
        migrations.AddField(
            model_name='feedback',
            name='match',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='matchup.Match'),
        ),
        migrations.AddField(
            model_name='feedback',
            name='player',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='feedback',
            name='reviewer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviewed_feedbacks', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='court',
            name='park',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='matchup.Park'),
        ),
        migrations.AddField(
            model_name='ammenity',
            name='parks',
            field=models.ManyToManyField(to='matchup.HendersonPark'),
        ),
    ]
