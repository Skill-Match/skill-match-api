import cloudinary
import cloudinary.uploader
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_save
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

    if created:
        if not instance.avatar:
            if instance.gender == 'Female':
                instance.avatar = cloudinary.CloudinaryImage("Woman_ibpgkk.png")
            else:
                instance.avatar = cloudinary.CloudinaryImage("Man_cqggt4.png")
            instance.save()

# @receiver(post_save, sender=Profile)
# def add_profile_image(sender, instance=None, created=False, **kwargs):
#     """
#     When created, if no avatar(picture) is uploaded, adds female default if
#     female. Otherwise default in model is set to male.
#     """
#     if created:
#         if not instance.avatar and instance.gender == 'Female':
#             instance.pic_url = 'http://res.cloudinary.com/skill-match/image/upload/c_scale,w_200/v1451856777/Woman_ibpgkk.png'
#             instance.small_pic_url = 'http://res.cloudinary.com/skill-match/image/upload/c_scale,w_50/v1451856777/Woman_ibpgkk.png'
#             instance.save()
#
# @receiver(pre_save, sender=Profile)
# def check_and_add_profile_image(sender, instance=None, created=False, **kwargs):
#     """
#         Creates custom pic_url's for the profile using cloudinary when an avatar is
#         uploaded.
#         Ineffecient because it uploads an additional image to cloudinary so there
#         are 2 uploads. Just a workaround at the moment.
#     """
#     if instance.avatar:
#         profile = Profile.objects.get(pk=instance.id)
#         if not instance.avatar == profile.avatar:
#             image = cloudinary.uploader.upload(instance.avatar)
#             split_url = image['url'].partition('upload/')
#             small_img_url = split_url[0] + split_url[1] + 'c_fill,g_face,h_050,r_23,w_050/' + split_url[2]
#             img_url = split_url[0] + split_url[1] + 'bo_1px_solid_rgb:747680,c_fill,g_face,h_200,r_4,w_200/' + split_url[2]
#             instance.pic_url = img_url
#             instance.small_pic_url = small_img_url
