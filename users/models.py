from cloudinary import CloudinaryImage
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

from django.db import models
from matchup.models import Feedback


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
    # pic_url = models.URLField(max_length=300, default='http://res.cloudinary.com/skill-match/image/upload/c_scale,w_200/v1451856958/Man_cqggt4.png')
    # small_pic_url = models.URLField(max_length=300, default='http://res.cloudinary.com/skill-match/image/upload/c_scale,w_50/v1451856958/Man_cqggt4.png')
    wants_texts = models.BooleanField(default=False)
    phone_number = models.CharField(null=True, blank=True, max_length=15)

    @property
    def pic_url(self):
        url = self.avatar.url
        if url == 'http://res.cloudinary.com/skill-match/image/upload/v1451856958/Man_cqggt4.png':
            return 'http://res.cloudinary.com/skill-match/image/upload/c_scale,w_200/v1451856958/Man_cqggt4.png'
        elif url == 'http://res.cloudinary.com/skill-match/image/upload/v1451856777/Woman_ibpgkk.png':
            return 'http://res.cloudinary.com/skill-match/image/upload/c_scale,w_200/v1451856777/Woman_ibpgkk.png'
        else:
            split_url = url.partition('upload/')
            img_url = split_url[0] + split_url[1] + 'bo_1px_solid_rgb:747680,c_fill,g_face,h_200,r_4,w_200/' + split_url[2]
            return img_url

    @property
    def small_pic_url(self):
        url = self.avatar.url
        split_url = url.partition('upload/')
        img_url = split_url[0] + split_url[1] + 'c_fill,g_face,h_050,r_23,w_050/' + split_url[2]
        return img_url

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


class Skill(models.Model):
    """
    Skill process:
    1. Command calls for calculations on skill level for all players.

    Relationships:
    1. player(User)
    """
    player = models.ForeignKey(User)
    sport = models.CharField(max_length=40)
    skill = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2)
    sportsmanship = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2)
    punctuality = models.DecimalField(null=True, blank=True, max_digits=5, decimal_places=2)
    num_feedbacks = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True, null=True)

    def __str__(self):
        return "{}'s {} skill: {}".format(self.player.username, self.sport,
                                          self.skill)

    def calculate_skills(self):
        feedbacks = Feedback.objects.filter(match__sport=self.sport).\
            filter(player=self.player)
        skill_total = 0
        sportsmanship_total = 0
        count = 0
        for feedback in feedbacks:
            skill_total += feedback.skill
            sportsmanship_total += feedback.sportsmanship
            count += 1
        self.skill = skill_total / count
        self.sportsmanship = sportsmanship_total / count
        self.num_feedbacks = count
        self.save()