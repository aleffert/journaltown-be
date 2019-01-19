from django.contrib.auth.models import User
from posts.models import Post
from rest_framework import serializers


class CurrentUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        email = serializers.EmailField()

        model = User
        fields = ('id', 'username', 'email')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class PostSerializer(serializers.HyperlinkedModelSerializer):

    author = UserSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'author', 'created_at', 'title', 'body', 'last_modified')
