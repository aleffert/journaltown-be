from django.contrib.auth import get_user_model
from rest_framework import generics
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from posts import filters
from posts import models
from posts import permissions
from posts import serializers
from posts import tasks
from posts.views.mixins import UsernameScopedMixin


class CurrentUserView(generics.GenericAPIView):
    """
    Lists information related to the current user.
    """
    serializer_class = serializers.CurrentUserSerializer
    permission_classes = (IsAuthenticated, )

    def get(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class UserViewSet(
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = (IsAuthenticated, permissions.IsUserOrReadOnly)
    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = 'username'


class FollowView(generics.GenericAPIView, UsernameScopedMixin):
    permission_classes = (IsAuthenticated, permissions.IsUserOrReadOnly)

    def get(self, request: Request, username: str, *args, **kwargs):
        user = self.get_user_or_404(username)

        followers = filters.FollowersFilterSet(request.GET, queryset=user.followers).qs
        return Response([serializers.UserSerializer(follow.follower).data for follow in followers])

    def put(self, request: Request, username: str, *args, **kwargs):
        source_user = self.get_user_or_404(username)

        target_username = request.data.get('username', None)
        target_user = self.get_user_or_404(target_username, check=False)

        follow = models.Follow.objects.filter(follower=source_user, followee=target_user).first()
        if not follow:
            follow = models.Follow.objects.create(follower=source_user, followee=target_user)
            tasks.send_follow_email(follow, self.request.user)

        return Response([serializers.RelatedUserSerializer(target_user).data], status=200)

    def delete(self, request: Request, username: str, *args, **kwargs):
        source_user = self.get_user_or_404(username)

        target_username = request.data.get('username', None)
        target_user = self.get_user_or_404(target_username, check=False)

        follows = models.Follow.objects.filter(follower=source_user, followee=target_user)
        follows.delete()

        return Response('', status=204)
