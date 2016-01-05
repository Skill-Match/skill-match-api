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
    DEFAULT_MALE_IMG_URL = 'http://res.cloudinary.com/skill-match/image/' \
                           'upload/v1/image/upload/%3Cimg%20src%3D%22http://' \
                           'res.cloudinary.com/skill-match/image/upload/' \
                           'Man_cqggt4.png"/>'

    DEFAULT_FEMALE_IMG_URL = 'http://res.cloudinary.com/skill-match/image/' \
                             'upload/v1/image/upload/%3Cimg%20src%3D%22http:' \
                             '//res.cloudinary.com/skill-match/image/upload/' \
                             'Woman_ibpgkk.png"/>'
    IMG_URL_ADD_ON = 'bo_1px_solid_rgb:747680,c_fill,g_face,h_200,r_4,w_200/'
    SMALL_IMG_URL_ADD_ON = 'c_fill,g_face,h_050,r_23,w_050/'

    user = models.OneToOneField(User)
    gender = models.CharField(max_length=8, choices=GENDER_CHOICES,
                              default=MALE)
    age = models.CharField(max_length=8, choices=AGE_CHOICES)
    avatar = CloudinaryField('image', null=True, blank=True)
    wants_texts = models.BooleanField(default=False)
    phone_number = models.CharField(null=True, blank=True, max_length=15)

    @property
    def pic_url(self):
        url = self.avatar.url
        if url == self.DEFAULT_MALE_IMG_URL:
            return 'http://res.cloudinary.com/skill-match/image/upload/' \
                   'c_scale,w_200/v1451856958/Man_cqggt4.png'
        elif url == self.DEFAULT_FEMALE_IMG_URL:
            return 'http://res.cloudinary.com/skill-match/image/upload/' \
                   'c_scale,w_200/v1451856777/Woman_ibpgkk.png'
        else:
            split_url = url.partition('upload/')
            img_url = split_url[0] + split_url[1] + self.IMG_URL_ADD_ON + \
                      split_url[2]
            return img_url

    @property
    def small_pic_url(self):
        url = self.avatar.url
        if url == self.DEFAULT_MALE_IMG_URL:
            return 'http://res.cloudinary.com/skill-match/image/upload/' \
                   'c_scale,w_50/v1451856777/Man_cqggt4.png'
        elif url == self.DEFAULT_FEMALE_IMG_URL:
            return 'http://res.cloudinary.com/skill-match/image/upload/' \
                   'c_scale,w_50/v1451856777/Woman_ibpgkk.png'
        split_url = url.partition('upload/')
        img_url = split_url[0] + split_url[1] + self.SMALL_IMG_URL_ADD_ON + \
                  split_url[2]
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

    def calculate(self):
        """
        All feedbacks for a certain sport are tallied to calculate the
        skill and sportsmanship.
        Skills are calculated based on the reviewers credibility. The reviewer's
        skill, sportsmanship, and xp (num_feedbacks) influence how much their
        feedback will be weighted.
        :return:
        """
        feedbacks = Feedback.objects.filter(match__sport=self.sport).\
            filter(player=self.player)

        skill_total = 0
        sportsmanship_total = 0
        total_weight = 0
        count = 0
        for feedback in feedbacks:
            # Get reviewer skill, sportsmanship, and num_feedbacks to determine
            # how his/her feedback should be weighted
            reviewer_cred = feedback.reviewer.skill_set.filter(sport=self.sport)
            if reviewer_cred:
                reviewer_cred = reviewer_cred[0]
                xp = reviewer_cred.num_feedbacks
                sportsmanship = reviewer_cred.sportsmanship
                skill = reviewer_cred.skill
            else:
                #give default values for new or unranked users
                xp = 0
                sportsmanship = 40
                skill = 40

            # Calculate weight based on reviewer credibility
            if 0 <= xp <= 10:
                weight = 3
            elif 11 < xp < 20:
                weight = 5
            elif 21 < xp < 30:
                weight = 7
            elif 31 < 40:
                weight = 8
            elif 41 < 50:
                weight = 9
            else:
                weight = 10

            # Weight for sportsmanship and skill are heavier than xp. Thus * 2
            # This breaks down to 40% skill, 40% sportsmanship, 20% xp
            weight += int((sportsmanship * 2) / 10)
            weight += int((skill * 2) / 10)
            total_weight += weight

            skill_total += feedback.skill * weight
            sportsmanship_total += feedback.sportsmanship * weight
            count += 1

        self.skill = skill_total / total_weight
        self.sportsmanship = sportsmanship_total / total_weight
        self.num_feedbacks = count
        self.save()
