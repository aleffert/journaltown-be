import secrets

from django.contrib.auth.models import User
from django.db import models


def generate_registration_token():
    return secrets.token_hex(nbytes=8)


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
