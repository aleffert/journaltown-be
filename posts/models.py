from django.contrib.auth.models import User
from django.db import models


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
