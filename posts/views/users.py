from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.response import Response

from posts import serializers


class CurrentUserView(generics.GenericAPIView):
    """
    Lists information related to the current user.
    """
    serializer_class = serializers.CurrentUserSerializer

    def get(self, request: Request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all()
    serializer_class = serializers.UserSerializer
