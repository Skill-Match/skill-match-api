from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from matchup.models import Match
from rest_framework.authtoken.models import Token
import sendgrid
from skill_match.settings import SENDGRID_KEY
from users.models import Profile


@receiver(post_save, sender=User)
def create_user_token(sender, instance=None, created=False, **kwargs):
    """
        When User object is created, Token with 1to1 is created for that user.
    """
    if created:
        Token.objects.create(user=instance)


@receiver(post_save, sender=Match)
def send_email(sender, instance=None, created=False, **kwargs):

    if created:
        user_email = instance.creator.email
        park_name = instance.park.name
        sport = instance.sport
        date = instance.date.strftime("%A %B, %d")
        time = instance.time.strftime("%I:%M %p")

        body_message = "You have succesfully created a match. You want to " \
                       "play {} at {} on {} at {}. We'll let you know if " \
                       "someone joins your match!".format(sport, park_name,
                                                          date, time)

        sg = sendgrid.SendGridClient(SENDGRID_KEY)

        message = sendgrid.Mail()
        message.add_to(user_email)
        message.set_subject(
            'Hi from SkillMatch!'
        )
        message.set_html("<p> " + body_message + "</p>")
        message.set_text(body_message)
        message.set_from('SkillMatch <fredoflynn@gmail.com>')
        status, msg = sg.send(message)


@receiver(post_save, sender=Profile)
def add_profile_image(sender, instance=None, created=False, **kwargs):
    pass


# @receiver(post_save, sender=Parent)
# def upload_picture_cloudinary(sender,instance=None, created=False, **kwargs):
#     if created:
#             if instance.profile_picture and (hasattr(instance.profile_picture, 'path')):
#                 image = cloudinary.uploader.upload(instance.profile_picture.path)
#                 if instance.profile_picture != "http://res.cloudinary.com/dpkceqvfi/image/upload/v1450429700/default_profile_ru96fo.png":
#                     print("original url" + instance.picture_url)
#                     instance.picture_url = image.get('url')
#                     print("this is the new url" + instance.picture_url)
#                     instance.save()
#             else:
#                 print("has no image")