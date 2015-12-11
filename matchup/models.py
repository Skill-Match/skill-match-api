from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Park(models.Model):
    rating = models.FloatField(null=True, blank=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    yelp_id = models.CharField(null=True, blank=True, max_length=100)
    mobile_url = models.URLField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    display_address1 = models.CharField(max_length=40, null=True, blank=True)
    display_address2 = models.CharField(max_length=40, null=True, blank=True)
    display_address3 = models.CharField(max_length=40, null=True, blank=True)
    postal_code = models.CharField(max_length=10, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    state_code = models.CharField(max_length=5, null=True, blank=True)

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
    is_confirmed = models.NullBooleanField(null=True, default=False)
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


# class Court(models.Model):
#     number = models.IntegerField()
#     park = models.ForeignKey(Park)
#     availability = models.FloatField()