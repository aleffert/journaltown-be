from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from posts.models import Post
from posts import filters
from posts import serializers


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows posts to be viewed or edited.
    """
    permission_classes = (IsAuthenticated, )
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer

    filterset_class = filters.PostFilterSet

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
