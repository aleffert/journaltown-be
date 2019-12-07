from typing import Callable, List

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

from posts.utils.dict import without


def _update_members(
    getter: Callable[[str], models.User], group: models.FriendGroup, member_usernames: List[str]
) -> List[models.FriendGroupMember]:
    members = [
        getter(member_username)
        for member_username in member_usernames
    ]

    existing_members = models.FriendGroupMember.objects.filter(group=group)
    for existing_member in existing_members:
        if existing_member.member.username not in member_usernames:
            existing_member.delete()

    for member in members:
        record = models.FriendGroupMember.objects.filter(group=group, member=member)
        if not record:
            models.FriendGroupMember.objects.create(group=group, member=member)

    return members


class FriendGroupsView(generics.GenericAPIView, UsernameScopedMixin):
    permission_classes = (IsAuthenticated, permissions.IsUser)

    def get(self, request: Request, username: str, *args, **kwargs):
        user = self.get_user_or_404(username)

        groups = models.FriendGroup.objects.filter(owner=user)

        return Response([serializers.FriendGroupSerializer(group).data for group in groups])

    def post(self, request: Request, username: str, *args, **kwargs):
        user = self.get_user_or_404(username)

        name = request.data.get('name', None)
        if not name:
            raise errors.ResponseException(errors.MissingFieldsError(['name']), 403)
        current_group = models.FriendGroup.objects.filter(owner=user, name=name).first()
        if current_group:
            raise errors.ResponseException(errors.NameInUseError(['name']), 403)

        group_data = without(request.data, ['members'])
        group = serializers.FriendGroupSerializer(data=group_data)
        group.is_valid(raise_exception=True)

        group_record = group.save(owner=request.user)

        member_usernames = request.data.get('members', None)
        if member_usernames:
            member_records = _update_members(
                lambda u: self.get_user_or_404(u, check=False),
                group_record, member_usernames
            )
            members = [
                serializers.RelatedUserSerializer(member).data for member in member_records
            ]

            return Response(dict(**group.data, **{'members': members}), status=201)
        else:
            return Response(group.data, status=201)


class FriendGroupView(generics.GenericAPIView, UsernameScopedMixin):
    permission_classes = (IsAuthenticated, permissions.IsUser)

    def get(self, request: Request, username: str, group_id: int, *args, **kwargs):
        user = self.get_user_or_404(username)
        current_group = get_object_or_404(models.FriendGroup, owner=user, pk=group_id)

        return Response(serializers.FriendGroupSerializer(current_group, expanded_fields='members').data)

    def put(self, request: Request, username: str, group_id: int, *args, **kwargs):
        user = self.get_user_or_404(username)
        current_group = get_object_or_404(models.FriendGroup, owner=user, pk=group_id)

        group_data = without(request.data, ['members'])
        group = serializers.FriendGroupSerializer(current_group, data=group_data)
        group.is_valid(raise_exception=True)

        group.save(owner=request.user)

        group_record = group.save(owner=request.user)

        member_usernames = request.data.get('members', None)
        if member_usernames:
            member_records = _update_members(
                lambda u: self.get_user_or_404(u, check=False), group_record, member_usernames
            )
            members = [
                serializers.RelatedUserSerializer(member).data for member in member_records
            ]

            return Response(dict(**group.data, **{'members': members}))
        else:
            return Response(group.data)

    def delete(self, request: Request, username: str, group_id: int, *args, **kwargs):
        user = self.get_user_or_404(username)
        current_group = get_object_or_404(models.FriendGroup, owner=user, pk=group_id)
        current_group.delete()

        return Response('', status=204)


class FriendGroupMemberView(generics.GenericAPIView, UsernameScopedMixin):
    permission_classes = (IsAuthenticated, permissions.IsUser)

    def get(self, request: Request, username: str, group_id: int, *args, **kwargs):
        user = self.get_user_or_404(username)
        group = get_object_or_404(models.FriendGroup, owner=user, id=group_id)

        members = models.FriendGroupMember.objects.filter(group=group)

        return Response([serializers.RelatedUserSerializer(record.member).data for record in members])

    def put(self, request: Request, username: str, group_id: int, *args, **kwargs):
        user = self.get_user_or_404(username)
        group = get_object_or_404(models.FriendGroup, owner=user, id=group_id)

        member_usernames = request.data.get('usernames', [])
        members = _update_members(lambda u: self.get_user_or_404(u, check=False), group, member_usernames)

        return Response([
            serializers.RelatedUserSerializer(member).data for member in members
        ])
