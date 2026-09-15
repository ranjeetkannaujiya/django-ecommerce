from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from base.models import BaseModel


# Profile is the user extension used for e-commerce-specific data.
# It keeps the auth user model clean while storing profile details, email status,
# and customer-specific order/account metadata.
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


# Signal-based profile creation ensures every new Django user gets a matching
# e-commerce profile automatically. This is a common backend pattern for
# onboarding and account verification without writing logic in the view layer.
@receiver(post_save, sender=User)
def create_profile_and_send_activation_email(
    sender,
    instance,
    created,
    **kwargs
):
    if not created:
        return

    profile, profile_created = Profile.objects.get_or_create(
        user=instance
    )

