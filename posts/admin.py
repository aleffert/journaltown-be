from django.contrib import admin
from posts import models


@admin.register(models.Post)
class PostAdmin(admin.ModelAdmin):
    pass


@admin.register(models.UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    pass
