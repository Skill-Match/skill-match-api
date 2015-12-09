from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Park(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Match(models.Model):
    creator = models.ForeignKey(User)
    description = models.TextField(max_length=1000, null=True, blank=True)
    park = models.ForeignKey(Park)
    sport = models.CharField(max_length=25)
    skill_level = models.PositiveIntegerField()
    date = models.DateField(null=True)
    time = models.TimeField(null=True)
    players = models.ManyToManyField(User, related_name='players', blank=True)
    is_open = models.NullBooleanField(null=True, default=True)
    is_completed = models.NullBooleanField(null=True, default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "{}'s {} match, match #{}".format(self.creator.username,
                                                 self.sport, self.id)



class Feedback(models.Model):
    reviewer = models.ForeignKey(User)
    player = models.ForeignKey(User, related_name='player')
    match = models.ForeignKey(Match)
    skill = models.IntegerField()
    sportsmanship = models.IntegerField()
    availability = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}'s review: {} skill: {}".format(self.reviewer.username,
                                                  self.player.username,
                                                  self.skill)