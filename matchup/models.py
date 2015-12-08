from django.contrib.auth.models import User
from django.db import models


class Park(models.Model):
    name = models.CharField(max_length=50)


class Match(models.Model):
    creator = models.ForeignKey(User, related_name='creator')
    players = models.ManyToManyField(User)
    park = models.ForeignKey(Park)
    created_at = models.DateTimeField(auto_now_add=True)


class Feedback(models.Model):
    reviewer = models.ForeignKey(User)
    player = models.ForeignKey(User, related_name='player')
    match = models.ForeignKey(Match)
    park = models.ForeignKey(Park)
    skill = models.IntegerField()
    sportsmanship = models.IntegerField()
    availablity = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)