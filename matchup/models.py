from django.contrib.auth.models import User
from django.db import models


class Park(models.Model):
    name = models.CharField(max_length=50)


class Match(models.Model):
    creator = models.ForeignKey(User, related_name='creator', null=True)
    title = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    park = models.ForeignKey(Park)
    sport = models.CharField(max_length=25, null=True)
    skill_level = models.IntegerField(null=True)
    date_time = models.DateTimeField(null=True)
    players = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)



class Feedback(models.Model):
    reviewer = models.ForeignKey(User)
    player = models.ForeignKey(User, related_name='player')
    match = models.ForeignKey(Match)
    park = models.ForeignKey(Park)
    skill = models.IntegerField()
    sportsmanship = models.IntegerField()
    availability = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
