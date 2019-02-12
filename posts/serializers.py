from django.contrib.auth.models import User
from drf_writable_nested import WritableNestedModelSerializer
from expander import ExpanderSerializerMixin
from rest_framework import serializers

from posts.models import Post, UserProfile, Follow


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

class RelatedUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username']

class FollowerUserSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source='follower.username')

    class Meta:
        model = Follow
        fields = ['username']


class FollowingUserSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source='followee.username')

    class Meta:
        model = Follow
        fields = ['username']


class UserSerializer(ExpanderSerializerMixin, WritableNestedModelSerializer):

    username = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ['id', 'username']
        expandable_fields = {
            'profile': UserProfileSerializer,
            'followers': (FollowerUserSerializer, (), {'many': True}),
            'following': (FollowingUserSerializer, (), {'many': True})
        }


class PostSerializer(serializers.ModelSerializer):

    author = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'created_at', 'title', 'body', 'last_modified']
