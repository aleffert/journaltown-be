from django.contrib.auth.models import User
from drf_writable_nested import WritableNestedModelSerializer
from expander import ExpanderSerializerMixin
from rest_framework import serializers

from posts.models import FriendGroup, Post, UserProfile, Follow, FriendGroupMember


class RelatedUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['bio']


class FriendGroupMemberUserSerializer(RelatedUserSerializer):

    username = serializers.CharField(source='member.username')

    class Meta:
        model = FriendGroupMember
        fields = ['username']


class FriendGroupSerializer(ExpanderSerializerMixin, serializers.ModelSerializer):

    name = serializers.CharField(required=True)

    class Meta:
        model = FriendGroup
        fields = ['id', 'name']

        expandable_fields = {
            'members': (FriendGroupMemberUserSerializer, (), {'many': True, 'source': 'friendgroupmember_set'}),
            'owner': (RelatedUserSerializer, (), {'read_only': True})
        }


class CurrentUserSerializer(serializers.ModelSerializer):

    profile = UserProfileSerializer(read_only=True)
    groups = FriendGroupSerializer(source="friendgroup_set", read_only=True, many=True)

    class Meta:
        email = serializers.EmailField()

        model = User
        fields = ['id', 'username', 'email', 'profile', 'groups']


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
