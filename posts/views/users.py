from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

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
    permission_classes = (IsAuthenticated, )
    queryset = get_user_model().objects.all()
    serializer_class = serializers.UserSerializer
    lookup_field = 'username'
