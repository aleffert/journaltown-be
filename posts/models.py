import secrets

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


def generate_registration_token():
    return secrets.token_hex(nbytes=8)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    last_modified = models.DateTimeField(
        auto_now=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    bio = models.CharField(max_length=1024 * 10, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


class Post(models.Model):

    author = models.ForeignKey(
        User,
        null=False,
        db_index=True,
        on_delete=models.CASCADE
    )

    last_modified = models.DateTimeField(
        auto_now=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    title = models.CharField(max_length=1024, blank=True, null=False)

    body = models.CharField(max_length=1024 * 1024, blank=True, null=False)

    def __str__(self):
        return f"Post by {self.author.username}: '{self.title[0:20]}'"


class EmailVerificationToken(models.Model):
    token = models.CharField(max_length=20, null=False, default=generate_registration_token)
    email = models.CharField(max_length=255, null=False)

    last_modified = models.DateTimeField(
        auto_now=True,
        null=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        null=False
    )


class Follow(models.Model):
    follower = models.ForeignKey(
        User,
        null=False, db_index=True, on_delete=models.CASCADE,
        related_name='followed_by_set'
    )

    followee = models.ForeignKey(
        User, null=False, db_index=True, on_delete=models.CASCADE,
        related_name='following_set'
    )

    last_modified = models.DateTimeField(
        auto_now=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.follower.username} follows {self.followee.username}"
