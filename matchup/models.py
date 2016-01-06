from django.contrib.auth.models import User
from django.contrib.gis.db import models


from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

#SPORT CHOICES for multiple models
TENNIS = 'Tennis'
BASKETBALL = 'Basketball'
FOOTBALL = 'Football'
SOCCER = 'Soccer'
VOLLEYBALL = 'Volleyball'
PICKLEBALL = 'Pickleball'
OTHER = 'Other'
SPORT_CHOICES = (
    (TENNIS, 'Tennis'),
    (BASKETBALL, 'Basketball'),
    (FOOTBALL, 'Football'),
    (SOCCER, 'Soccer'),
    (VOLLEYBALL, 'Volleyball'),
    (PICKLEBALL, 'Pickleball'),
    (OTHER, 'Other')
)

DEFAULT_IMG = 'http://res.cloudinary.com/skill-match/image/upload/' \
              'v1451804013/trophy_200_cnaras.jpg'
TENNIS_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                 "c_scale,w_200/v1451803727/1451824644_tennis_jegpea.png"
BASKETBALL_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                     "c_scale,w_200/v1451811954/basketball_lxzgmw.png"
FOOTBALL_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                   "c_scale,w_200/v1451812093/American-Football_vbp5ww.png"
SOCCER_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                 "c_scale,w_200/v1451803724/1451824570_soccer_mwvtwy.png"
VOLLEYBALL_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                     "c_scale,w_200/v1451803790/1451824851_" \
                     "volleyball_v2pu0m.png"
PICKLEBALL_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                     "c_scale,w_200/v1451803795/1451824990_" \
                     "table_tennis_uqv436.png"
TROPHY_IMG_URL = "http://res.cloudinary.com/skill-match/image/upload/" \
                "v1451804013/trophy_200_cnaras.jpg"


class Park(models.Model):
    """
    Currently borrowed from YELP API.
    Some are linked via OneToOne with HendersonParks
    """
    rating = models.FloatField()
    rating_img_url = models.URLField(max_length=300)
    rating_img_url_small = models.URLField(max_length=300)
    name = models.CharField(max_length=200)
    url = models.URLField()
    image_url = models.URLField(null=True, blank=True)
    city = models.CharField(max_length=50)
    display_address1 = models.CharField(max_length=40)
    display_address2 = models.CharField(max_length=40, null=True, blank=True)
    display_address3 = models.CharField(max_length=40, null=True, blank=True)
    postal_code = models.CharField(max_length=10)
    location = models.PointField()
    state_code = models.CharField(max_length=5)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def latitude(self):
        latitude = self.location.coords[1]
        return latitude

    @property
    def longitude(self):
        longitude = self.location.coords[0]
        return longitude


class HendersonPark(models.Model):
    """
    Scraped with permission from Henderson Parks and Rec Website
    """
    park = models.ForeignKey(Park, null=True, blank=True,
                             related_name='henderson_park')
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=150)
    url = models.URLField()
    img_url = models.URLField(null=True, blank=True, max_length=350)
    created_on = models.DateTimeField(auto_now_add=True)
    modifided_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Ammenity(models.Model):
    """
    Also scraped from Henderson Parks and Rec.
    ManyToMany Relationship with HendersonPark
    Example ammenities: 'Open Grass Field', 'Lighted Tennis Courts'
    """
    name = models.CharField(max_length=125)
    parks = models.ManyToManyField(HendersonPark)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Match(models.Model):
    """
    Process for Match:
    1. User create match with park, sport, date, time, skill level wanted.
    2. Creation process add user as creator and player on players many to many.
    3. A different User signs up. If Tennis, Match is now closed
        (is_open=False)
    4. If tennis, User may confirm or decline match. If user accepts it is
        confirmed. (is_confirmed=True). If user declines, it opens
        (is_open=True)
    5. When date and time expire, a command will close "complete match",
        (is_completed=True)

    Relationships:
    1. creator(User)
    2. players(User(s), m2m)
    3. park(Park)

    Model needs cleanup to lose most booleans and instead have a choice flow
    for match "status" like OPEN -> JOINED -> CONFIRMED -> COMPLETED
    """
    creator = models.ForeignKey(User, related_name='created_matches')
    description = models.TextField(max_length=1000, null=True, blank=True)
    park = models.ForeignKey(Park)
    sport = models.CharField(max_length=25, choices=SPORT_CHOICES,
                             default=TENNIS)
    other = models.CharField(max_length=25, null=True, blank=True)
    skill_level = models.PositiveIntegerField()
    date = models.DateField()
    time = models.TimeField()
    players = models.ManyToManyField(User, blank=True)
    img_url = models.URLField(max_length=200, default=DEFAULT_IMG)
    is_open = models.BooleanField(default=True)
    is_completed = models.BooleanField(default=False)
    is_confirmed = models.BooleanField(default=False)
    is_challenge = models.BooleanField(default=False)
    challenge_declined = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return "{}'s {} match, match #{}".format(self.creator.username,
                                                 self.sport, self.id)


@receiver(post_save, sender=Match)
def add_profile_image(sender, instance=None, created=False, **kwargs):

    if created:
        if instance.sport == 'Tennis':
            instance.img_url = TENNIS_IMG_URL
        elif instance.sport == 'Basketball':
            instance.img_url = BASKETBALL_IMG_URL
        elif instance.sport == 'Football':
            instance.img_url = FOOTBALL_IMG_URL
        elif instance.sport == 'Soccer':
            instance.img_url = SOCCER_IMG_URL
        elif instance.sport == 'Volleyball':
            instance.img_url = VOLLEYBALL_IMG_URL
        elif instance.sport == 'Pickleball':
            instance.img_url = PICKLEBALL_IMG_URL
        else:
            instance.img_url = TROPHY_IMG_URL
        instance.save()


class Feedback(models.Model):
    """
    Feedback process:
    1. User inputs skill level(1-100), sportsmanship level(1-100), crowd level
        (1-5), and punctuality.
    2. Creation process adds player being reviewed(through match relationship,
        and reviewer through request.

    Relationships:
    1. reviewer(User)
    2. player(User) - being reviewed
    3. match(Match)

    """
    NO_SHOW = 'No Show'
    ON_TIME = 'On Time'
    LITTLE_LATE = 'Little bit late'
    LATE = 'Late'
    PUNCTUALITY_CHOICES = (
        (NO_SHOW, 'No Show'),
        (ON_TIME, 'On Time'),
        (LITTLE_LATE, 'Little bit late'),
        (LATE, 'Over 10 min late')
    )

    reviewer = models.ForeignKey(User, related_name='reviewed_feedbacks')
    player = models.ForeignKey(User)
    match = models.ForeignKey(Match)
    skill = models.PositiveIntegerField()
    sportsmanship = models.PositiveIntegerField()
    availability = models.PositiveIntegerField()
    punctuality = models.CharField(max_length=15,
                                   choices=PUNCTUALITY_CHOICES,
                                   default=ON_TIME)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return "{}'s review: {} skill: {}".format(self.reviewer.username,
                                                  self.player.username,
                                                  self.skill)


class Court(models.Model):
    #in the future add ranking
    park = models.ForeignKey(Park, null=True, blank=True)
    sport = models.CharField(max_length=25, choices=SPORT_CHOICES)
    other = models.CharField(max_length=25, null=True, blank=True)
    num_courts = models.IntegerField(null=True, blank=True)
    img_url = models.URLField(default=DEFAULT_IMG)
    location = models.PointField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} at {}".format(self.sport, self.park.name)

    @property
    def small_sport_img(self):
        split_url = self.img_url.partition('c_scale,w_200/')
        small_sport_img = split_url[0] + \
                          'c_scale,h_50,w_50/' + split_url[2]
        return small_sport_img


@receiver(post_save, sender=Court)
def add_profile_image(sender, instance=None, created=False, **kwargs):

    if created:
        if instance.sport == 'Tennis':
            instance.img_url = TENNIS_IMG_URL
        elif instance.sport == 'Basketball':
            instance.img_url = BASKETBALL_IMG_URL
        elif instance.sport == 'Football':
            instance.img_url = FOOTBALL_IMG_URL
        elif instance.sport == 'Soccer':
            instance.img_url = SOCCER_IMG_URL
        elif instance.sport == 'Volleyball':
            instance.img_url = VOLLEYBALL_IMG_URL
        elif instance.sport == 'Pickleball':
            instance.img_url = PICKLEBALL_IMG_URL
        else:
            instance.img_url = TROPHY_IMG_URL
        instance.save()