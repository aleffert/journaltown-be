from django.contrib.auth.models import User
from drf_writable_nested import WritableNestedModelSerializer
from expander import ExpanderSerializerMixin
from rest_framework import serializers

from posts.models import Post, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['bio']


class CurrentUserSerializer(serializers.ModelSerializer):

    profile = UserProfileSerializer(read_only=True)

    class Meta:
        email = serializers.EmailField()

        model = User
        fields = ['id', 'username', 'email', 'profile']


class UserSerializer(ExpanderSerializerMixin, WritableNestedModelSerializer):

    username = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['id', 'username']
        expandable_fields = {
            'profile': UserProfileSerializer
        }


class PostSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'created_at', 'title', 'body', 'last_modified']
