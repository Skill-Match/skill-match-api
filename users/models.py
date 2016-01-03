from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

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
    avatar = CloudinaryField('image', null=True, blank=True)
    pic_url = models.URLField(max_length=300, default='http://res.cloudinary.com/skill-match/image/upload/c_scale,w_200/v1451856958/Man_cqggt4.png')
    small_pic_url = models.URLField(max_length=300, default='http://res.cloudinary.com/skill-match/image/upload/c_scale,w_50/v1451856958/Man_cqggt4.png')
    wants_texts = models.BooleanField(default=False)
    phone_number = models.CharField(null=True, blank=True, max_length=15)

    @property
    def sportsmanship(self):
        """Return average sportsmanship level over matches"""
        total = 0
        count = 0
        if self.user.skill_set.all():
            for skill in self.user.skill_set.all():
                total += skill.sportsmanship
                count += 1
            return total / count

        return None

    def __str__(self):
        return self.user.username