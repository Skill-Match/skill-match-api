from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


@receiver(post_save, sender=User)
def create_user_token(sender, instance=None, created=False, **kwargs):
    """
        When User object is created, Token with 1to1 is created for that user.
    """
    if created:
        Token.objects.create(user=instance)