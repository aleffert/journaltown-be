from django.contrib.auth import get_user_model
from rest_framework import views
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from posts import errors
from posts import models
from posts import permissions
from posts import serializers


class CurrentUserView(generics.GenericAPIView):
    """
    Lists information related to the current user.
    """
    serializer_class = serializers.CurrentUserSerializer
    permission_classes = (IsAuthenticated, )

    def get(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = (IsAuthenticated, permissions.IsUserOrReadOnly)
    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = 'username'


class FollowView(views.APIView):
    permission_classes = (IsAuthenticated, permissions.IsUserOrReadOnly)

    def get(self, request: Request, username: str, *args, **kwargs):
        user = get_user_model().objects.filter(username=username).first()
        if not user:
            return Response(errors.InvalidUsernameError(username).render(), 404)
        self.check_object_permissions(self.request, user)
        return Response([serializers.UserSerializer(follow.follower).data for follow in user.following_set.all()])

    def put(self, request: Request, username: str, *args, **kwargs):
        source_user = get_user_model().objects.filter(username=username).first()
        self.check_object_permissions(self.request, source_user)
        if not source_user:
            return Response(errors.InvalidUsernameError(username).render(), 404)

        target_username = request.data.get('username', None)
        if not target_username:
            return Response(errors.MissingFieldsError(['username']).render(), 400)

        target_user = get_user_model().objects.filter(username=target_username).first()
        if not target_user:
            return Response(errors.InvalidUsernameError(username).render(), 404)

        follow = models.Follow.objects.filter(follower=source_user, followee=target_user).first()
        if not follow:
            models.Follow.objects.create(follower=source_user, followee=target_user)

        return Response('', status=204)

    def delete(self, request: Request, username: str, *args, **kwargs):
        source_user = get_user_model().objects.filter(username=username).first()
        self.check_object_permissions(self.request, source_user)
        if not source_user:
            return Response(errors.InvalidUsernameError(username).render(), 404)

        target_username = request.data.get('username', None)
        if not target_username:
            return Response(errors.MissingFieldsError(['username']).render(), 400)

        target_user = get_user_model().objects.filter(username=target_username).first()
        if not target_user:
            return Response(errors.InvalidUsernameError(username).render(), 404)

        follows = models.Follow.objects.filter(follower=source_user, followee=target_user)
        follows.delete()

        return Response('', status=204)
