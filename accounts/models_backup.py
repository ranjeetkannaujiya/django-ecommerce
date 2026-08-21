from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid

from base.models import BaseModel
from base.emails import send_account_activation_email


class Profile(BaseModel):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    is_email_verified = models.BooleanField(
        default=False
    )

    email_token = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    profile_image = models.ImageField(
        upload_to="profile",
        blank=True,
        null=True
    )

    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True
    )

    def __str__(self):
        full_name = f"{self.user.first_name} {self.user.last_name}".strip()

        if full_name:
            return full_name
        return self.user.email


@receiver(post_save, sender=User)
def send_email_token(sender, instance, created, **kwargs):

    try:

        if created:

            email_token = str(uuid.uuid4())

            Profile.objects.create(
                user=instance,
                email_token=email_token
            )

            send_account_activation_email(
                instance.email,
                email_token
            )

    except Exception as e:
        print(e)