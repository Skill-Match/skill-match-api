from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    MALE = 'Male'
    FEMALE = 'Female'
    OTHER = 'Other'
    UNDER_16 = 'Under 16'
    TEEN = '16-19'
    TWENTIES = "20's"
    THIRTIES = "30's"
    FOURTIES = "40's"
    FIFTIES = "50's"
    SIXTY = "60+"
    GENDER_CHOICES = (
        (MALE, 'Man'),
        (FEMALE, 'Woman'),
        (OTHER, 'Other')
    )
    AGE_CHOICES = (
        (UNDER_16, 'Under 16'),
        (TEEN, '16-19'),
        (TWENTIES, "20's"),
        (THIRTIES, "30's"),
        (FOURTIES, "40's"),
        (FIFTIES, "50's"),
        (SIXTY, "60+")
    )

    user = models.OneToOneField(User)
    gender = models.CharField(max_length=8, choices=GENDER_CHOICES,
                              default=MALE)
    age = models.CharField(max_length=8, choices=AGE_CHOICES)

    @property
    def skill(self):
        total = 0
        count = 0
        if self.user.players.all():
            for match in self.user.players.all():
                feedbacks = match.feedback_set.filter(player=self.user)
                if feedbacks:
                    total += feedbacks[0].skill
                    count += 1
                    return round(total / count, 2)

        return None

    @property
    def sportsmanship(self):
        total = 0
        count = 0
        if self.user.players.all():
            for match in self.user.players.all():
                feedbacks = match.feedback_set.filter(player=self.user)
                if feedbacks:
                    total += feedbacks[0].sportsmanship
                    count += 1
                    return round(total / count, 2)

        return None

    def __str__(self):
        return self.user.username


    # @property
    # def skill(self):
    #     total = 0
    #     count = 0
    #     if self.user.players.all():
    #         for match in self.user.players.all():
    #             feedbacks = match.feedback_set.filter(player=self.user)
    #             if feedbacks:
    #                 total += feedbacks[0].skill
    #                 count += 1
    #         return round(total / count, 2)
    #
    #     return None