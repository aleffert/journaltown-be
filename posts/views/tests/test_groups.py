import json
from django.contrib.auth import get_user_model

from posts.tests.utils import AuthTestCase
from posts.models import FriendGroup, FriendGroupMember


class FriendGroupsViewTest(AuthTestCase):

    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(username='me', email='me@example.com')
        self.other = get_user_model().objects.create_user(username='other', email='other@example.com')

    def test_can_get_friend_groups(self):
        """We can get our own user's friend groups"""
        self.client.force_login(self.user)
        FriendGroup.objects.create(owner=self.user, name="Some Group")

        response = self.client.get(f'/users/{self.user.username}/groups/')

        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]['name'], 'Some Group')

    def test_cannot_get_other_user_friend_groups(self):
        """We cannot get another user's friend groups"""
        self.client.force_login(self.user)
        FriendGroup.objects.create(owner=self.other, name="Some Group")

        response = self.client.get(f'/users/{self.other.username}/groups/')

        self.assertEqual(response.status_code, 403)

    def test_can_create_own_group(self):
        """We can create a group for ourselves"""
        self.client.force_login(self.user)

        response = self.client.post(
            f'/users/{self.user.username}/groups/',
            data=json.dumps({'name': 'Some Group'}),
            content_type="application/json"
        )

        body = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(body['name'], 'Some Group')

    def test_create_group_needs_name(self):
        """Creating a group requires a name"""
        self.client.force_login(self.user)

        response = self.client.post(
            f'/users/{self.user.username}/groups/',
            data=json.dumps({}),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 403)

    def test_can_create_group_with_members(self):
        """Can create a group with members"""
        self.client.force_login(self.user)

        response = self.client.post(
            f'/users/{self.user.username}/groups/',
            data=json.dumps({
                'name': 'Some Group',
                'members': [self.other.username]
            }),
            content_type="application/json"
        )

        body = response.json()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(body['members'], [{'username': self.other.username}])

    def test_cannot_create_multiple_groups_with_same_name(self):
        """We cannot create multiple groups with the same name"""
        self.client.force_login(self.user)
        FriendGroup.objects.create(owner=self.user, name="Name")

        response = self.client.post(
            f'/users/{self.user.username}/groups/',
            data=json.dumps({'name': 'Name'}),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 403)


class FriendGroupViewTest(AuthTestCase):

    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(username='me', email='me@example.com')
        self.other = get_user_model().objects.create_user(username='other', email='other@example.com')

    def test_can_get_group(self):
        """We can fetch a group"""
        self.client.force_login(self.user)

        # Make the group
        response = self.client.post(
            f'/users/{self.user.username}/groups/',
            data=json.dumps({
                'name': 'Some Group',
                'members': [self.other.username]
            }),
            content_type="application/json"
        )

        group_id = response.json()['id']
        response = self.client.get(
            f'/users/{self.user.username}/groups/{group_id}/',
            content_type="application/json"
        )
        body = response.json()
        self.assertEqual('Some Group', body['name'])
        self.assertEqual([{'username': self.other.username}], body['members'])

    def test_can_change_group_name(self):
        """We can change a group's name"""
        self.client.force_login(self.user)

        group = FriendGroup.objects.create(owner=self.user, name="Some Group")

        response = self.client.put(
            f'/users/{self.user.username}/groups/{group.pk}/',
            data=json.dumps({'name': 'Some New Group'}),
            content_type="application/json"
        )

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body['name'], 'Some New Group')

    def test_can_delete_group(self):
        """We can delete a group we own"""
        self.client.force_login(self.user)

        group = FriendGroup.objects.create(owner=self.user, name="Some Group")

        response = self.client.delete(
            f'/users/{self.user.username}/groups/{group.pk}/',
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(FriendGroup.objects.filter(owner=self.other).count(), 0)

    def test_cannot_delete_group_under_other_username(self):
        """We cannot delete a group under someone else's username"""
        self.client.force_login(self.user)

        group = FriendGroup.objects.create(owner=self.other, name="Some Group")

        response = self.client.delete(
            f'/users/{self.other.username}/groups/{group.pk}/',
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 403)

    def test_cannot_delete_other_group(self):
        """We cannot delete a group under our username but owned by someone else"""
        self.client.force_login(self.user)

        group = FriendGroup.objects.create(owner=self.other, name="Some Group")

        response = self.client.delete(
            f'/users/{self.user.username}/groups/{group.pk}/',
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 404)

    def test_updating_group_can_remove_members(self):
        """Updating a group can remove members"""
        self.client.force_login(self.user)

        response = self.client.post(
            f'/users/{self.user.username}/groups/',
            data=json.dumps({
                'name': 'Some Group',
                'members': [self.other.username]
            }),
            content_type="application/json"
        )
        group_id = response.json()['id']

        response = self.client.put(
            f'/users/{self.user.username}/groups/{group_id}/',
            data=json.dumps({
                'name': 'Some Group',
                'members': []
            }),
            content_type="application/json"
        )

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body['members'], [])

    def test_updating_group_can_update_members(self):
        """Updating a group can change its members"""
        self.client.force_login(self.user)

        third = get_user_model().objects.create_user(username='third', email='third@example.com')

        response = self.client.post(
            f'/users/{self.user.username}/groups/',
            data=json.dumps({
                'name': 'Some Group',
                'members': [self.other.username]
            }),
            content_type="application/json"
        )
        group_id = response.json()['id']

        response = self.client.put(
            f'/users/{self.user.username}/groups/{group_id}/',
            data=json.dumps({
                'name': 'Some Group',
                'members': [third.username]
            }),
            content_type="application/json"
        )

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(body['members'], [{'username': third.username}])

    def test_updating_group_will_not_overwrite_members(self):
        """Updating a group won't overwrite members if we don't pass a members field"""
        self.client.force_login(self.user)

        response = self.client.post(
            f'/users/{self.user.username}/groups/',
            data=json.dumps({
                'name': 'Some Group',
                'members': [self.other.username]
            }),
            content_type="application/json"
        )

        group_id = response.json()['id']
        response = self.client.put(
            f'/users/{self.user.username}/groups/{group_id}/',
            data=json.dumps({
                'name': 'Some Group',
            }),
            content_type="application/json"
        )

        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('members', body)


class FriendGroupMemberViewTest(AuthTestCase):

    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(username='me', email='me@example.com')
        self.other = get_user_model().objects.create_user(username='other', email='other@example.com')
        self.group = FriendGroup.objects.create(owner=self.user, name="Some Group")
        self.other_group = FriendGroup.objects.create(name='A group', owner=self.other)

    def test_can_get_group_members(self):
        """We can get our own user's friend groups"""
        self.client.force_login(self.user)

        FriendGroupMember.objects.create(member=self.other, group=self.group)
        FriendGroupMember.objects.create(member=self.user, group=self.group)

        response = self.client.get(f'/users/{self.user.username}/groups/{self.group.pk}/members/')

        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(body), 2)
        self.assertIn({'username': 'me'}, body)
        self.assertIn({'username': 'other'}, body)

    def test_cannot_get_external_user_group_members(self):
        """We cannot get another user's friend groups"""
        self.client.force_login(self.user)

        FriendGroupMember.objects.create(member=self.user, group=self.other_group)

        response = self.client.get(f'/users/{self.other.username}/groups/{self.other_group.pk}/members/')

        self.assertEqual(response.status_code, 403)

    def test_cannot_get_other_user_group_members(self):
        """We cannot get another user's friend groups under our own namespace"""
        self.client.force_login(self.user)

        FriendGroupMember.objects.create(member=self.other, group=self.other_group)

        response = self.client.get(f'/users/{self.user.username}/groups/{self.other_group.pk}/members/')

        self.assertEqual(response.status_code, 404)

    def test_can_add_group_members(self):
        """We can add group members"""
        self.client.force_login(self.user)

        response = self.client.put(
            f'/users/{self.user.username}/groups/{self.group.pk}/members/',
            data=json.dumps({'usernames': [self.other.username]}),
            content_type='application/json'
        )

        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body, [{'username': self.other.username}])

    def test_can_add_group_members_idempotent(self):
        """Adding group members is idempotent"""
        self.client.force_login(self.user)

        response = self.client.put(
            f'/users/{self.user.username}/groups/{self.group.pk}/members/',
            data=json.dumps({'usernames': [self.other.username]}),
            content_type='application/json'
        )
        response = self.client.put(
            f'/users/{self.user.username}/groups/{self.group.pk}/members/',
            data=json.dumps({'usernames': [self.other.username]}),
            content_type='application/json'
        )

        body = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(body, [{'username': self.other.username}])
        self.assertEqual(1, FriendGroupMember.objects.count())

    def test_cannot_add_members_to_external_group(self):
        """Cannot add members to a group owned by another user through their namespace"""
        self.client.force_login(self.user)

        response = self.client.put(
            f'/users/{self.other.username}/groups/{self.group.pk}/members/',
            data=json.dumps({'username': self.user.username}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 403)

    def test_cannot_add_members_to_other_group(self):
        """Cannot add members to a group owned by another user through our namespace"""
        self.client.force_login(self.user)

        response = self.client.put(
            f'/users/{self.user.username}/groups/{self.other_group.pk}/members/',
            data=json.dumps({'username': self.user.username}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 404)

    def test_can_delete_members(self):
        """Can delete a group member"""
        self.client.force_login(self.user)

        FriendGroupMember.objects.create(member=self.other, group=self.group)

        response = self.client.put(
            f'/users/{self.user.username}/groups/{self.group.pk}/members/',
            data=json.dumps({'usernames': []}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(FriendGroupMember.objects.filter(member=self.other, group=self.group).first())

    def test_can_delete_members_idempotent(self):
        """Deleting a member from a group that member is not in is fine"""
        self.client.force_login(self.user)

        FriendGroupMember.objects.create(member=self.other, group=self.group)

        response = self.client.put(
            f'/users/{self.user.username}/groups/{self.group.pk}/members/',
            data=json.dumps({'usernames': []}),
            content_type='application/json'
        )

        response = self.client.put(
            f'/users/{self.user.username}/groups/{self.group.pk}/members/',
            data=json.dumps({'usernames': []}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(FriendGroupMember.objects.filter(member=self.other, group=self.group).first())

    def test_cannot_delete_members_from_external_group(self):
        """Cannot delete members from a group owned by another user through their namespace"""
        self.client.force_login(self.user)

        FriendGroupMember.objects.create(member=self.user, group=self.other_group)

        response = self.client.put(
            f'/users/{self.other.username}/groups/{self.group.pk}/members/',
            data=json.dumps({'usernames': [self.user.username]}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 403)

    def test_cannot_delete_members_from_other_group(self):
        """Cannot delete members from a group owned by another user through our namespace"""
        self.client.force_login(self.user)

        response = self.client.put(
            f'/users/{self.user.username}/groups/{self.other_group.pk}/members/',
            data=json.dumps({'usernames': [self.user.username]}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 404)
