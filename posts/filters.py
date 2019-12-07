import django_filters.rest_framework
from posts.models import Post


class CharInFilter(django_filters.rest_framework.BaseInFilter, django_filters.rest_framework.CharFilter):
    pass


class FollowersFilterSet(django_filters.rest_framework.FilterSet):
    username = django_filters.CharFilter(field_name='followee__username', lookup_expr='exact')
    username__in = CharInFilter(field_name='followee__username', lookup_expr='in')


class PostFilterSet(django_filters.rest_framework.FilterSet):

    class Meta:
        model = Post
        fields = {
            'created_at': ['lt', 'gt'],
            'last_modified': ['lt', 'gt'],
        }
