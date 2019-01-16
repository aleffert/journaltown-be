from django.contrib.auth.models import User
from posts.models import Post
from rest_framework import serializers


class CurrentUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        email = serializers.EmailField()

        model = User
        fields = ('username', 'email')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('username', )


class PostSerializer(serializers.HyperlinkedModelSerializer):

    author = serializers.PrimaryKeyRelatedField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    last_modified = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Post
        fields = ('id', 'author', 'created_at', 'title', 'body', 'last_modified')
