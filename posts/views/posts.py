from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from posts.models import Post
from posts import serializers


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    permission_classes = (IsAuthenticated, )
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    # def perform_update(self, serializer):
    #     if serializer.user != self.request.user:
    #         raise
    #         serializer.save()
