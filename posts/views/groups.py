from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from posts import errors
from posts import models
from posts import permissions
from posts import serializers
from posts.views.mixins import UsernameScopedMixin


class FriendGroupView(generics.GenericAPIView, UsernameScopedMixin):
    permission_classes = (IsAuthenticated, permissions.IsUser)

    def get(self, request: Request, username: str, *args, **kwargs):
        user = self.get_user_or_404(username)

        groups = models.FriendGroup.objects.filter(owner=user)

        return Response([serializers.FriendGroupSerializer(group).data for group in groups])

    def post(self, request: Request, username: str, *args, **kwargs):
        user = self.get_user_or_404(username)

        group = serializers.FriendGroupSerializer(data=request.data)
        group.is_valid()

        current_group = models.FriendGroup.objects.filter(owner=user, name=group.validated_data['name'])
        if current_group:
            group.save(current_group, owner=request.user)
        else:
            group.save(owner=request.user)

        return Response(group.data)

    def delete(self, request: Request, username: str, *args, **kwargs):
        user = self.get_user_or_404(username)

        group_id = request.data['id']
        if not group_id:
            return Response(errors.MissingFieldsError(['id']).render(), 404)

        current_group = models.FriendGroup.objects.filter(owner=user, id=group_id)
        if not current_group:
            return Response(errors.InvalidFieldsError(['id']).render(), 404)

        current_group.delete()

        return Response('', 204)


class FriendGroupMemberView(generics.GenericAPIView, UsernameScopedMixin):
    permission_classes = (IsAuthenticated, permissions.IsUser)

    def get(self, request: Request, username: str, group_id: int, *args, **kwargs):
        user = self.get_user_or_404(username)
        group = get_object_or_404(models.FriendGroup, owner=user, id=group_id)

        if group.owner != user:
            return Response(errors.InvalidFieldsError(['id']).render(), 404)

        members = models.FriendGroupMember.objects.filter(group=group)

        return Response([serializers.RelatedUserSerializer(record.member).data for record in members])

    def put(self, request: Request, username: str, group_id: int, *args, **kwargs):
        user = self.get_user_or_404(username)
        group = get_object_or_404(models.FriendGroup, owner=user, id=group_id)

        member_username = request.data.get('username', None)
        member = self.get_user_or_404(member_username, check=False)

        if group.owner != user:
            return Response(errors.InvalidFieldsError(['id']).render(), 404)

        record = models.FriendGroupMember.objects.filter(group=group, member=member)
        if not record:
            models.FriendGroupMember.objects.create(group=group, member=member)

        return Response(serializers.RelatedUserSerializer(member).data, 200)

    def delete(self, request: Request, username: str, group_id: int, *args, **kwargs):
        user = self.get_user_or_404(username)
        group = get_object_or_404(models.FriendGroup, owner=user, id=group_id)

        member_username = request.data.get('username', None)
        member = self.get_user_or_404(member_username, check=False)

        if group.owner != user:
            return Response(errors.InvalidFieldsError(['id']).render(), 404)

        record = models.FriendGroupMember.objects.filter(group=group, member=member)
        if record:
            record.delete()

        return Response('', 204)
