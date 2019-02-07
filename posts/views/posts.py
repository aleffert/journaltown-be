import django_filters.rest_framework
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from posts.models import Post
from posts import serializers


class PostFilters(django_filters.rest_framework.FilterSet):

    class Meta:
        model = Post
        fields = {
            'created_at': ['lt', 'gt'],
            'last_modified': ['lt', 'gt'],
        }


class PostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows posts to be viewed or edited.
    """
    permission_classes = (IsAuthenticated, )
    queryset = Post.objects.all()
    serializer_class = serializers.PostSerializer

    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_class = PostFilters

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
