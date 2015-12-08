from django.contrib.auth.models import User
from django.db import models


class Park(models.Model):
    name = models.CharField(max_length=50)


class Match(models.Model):
    creator = models.ForeignKey(User, related_name='creator')
    title = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(max_length=1000, null=True, blank=True)
    park = models.ForeignKey(Park)
    sport = models.CharField(max_length=25)
    skill_level = models.IntegerField()
    date_time = models.DateTimeField()
    players = models.ManyToManyField(User, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



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
