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

    def __str__(self):
        return self.user.username

