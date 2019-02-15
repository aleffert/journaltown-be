import logging
import json
from django.contrib.auth import get_user_model
from django.core import mail

from posts.tests.utils import AuthTestCase
from posts.models import Follow


class CurrentUserViewTest(AuthTestCase):

    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(username='me', email='me@example.com')
        self.other = get_user_model().objects.create_user(username='other', email='other@example.com')

    def test_not_logged_in_returns_unauthorized(self):
        response = self.client.get('/me/')
        self.assertEqual(401, response.status_code)

    def test_logged_in_returns_user_info(self):
        self.client.force_login(self.user)
        response = self.client.get('/me/')
        self.assertEqual(200, response.status_code)
        self.assertEqual({'username': 'me', 'id': self.user.id, 'email': 'me@example.com', 'profile': {
            'bio': None
        }}, response.json())

    def test_get_individual_user(self):
        """We should be able to fetch a user info by username"""
        self.client.force_login(self.user)
        response = self.client.get(f'/users/{self.user.username}/')
        body = response.json()
        self.assertEqual(body['username'], self.user.username)

    def test_get_individual_user_expand_profile(self):
        """We should be able to fetch a user's profile"""
        bio = "Some stuff about me"
        self.client.force_login(self.user)
        self.user.profile.bio = bio
        self.user.profile.save()
        response = self.client.get(f'/users/{self.user.username}/', {'expand': 'profile'})
        body = response.json()
        self.assertEqual(body['profile']['bio'], self.user.profile.bio)

    def test_get_user_includes_follows(self):
        self.client.force_login(self.user)
        Follow.objects.create(follower=self.user, followee=self.other)
        Follow.objects.create(follower=self.user, followee=self.user)
        response = self.client.get(f'/users/{self.user.username}/', {'expand': 'followers,following'})
        body = response.json()
        self.assertEqual(body['following'], [{'username': 'other'}, {'username': 'me'}])
        self.assertEqual(body['followers'], [{'username': 'me'}])

    def test_update_profile(self):
        """We should just be able to update a user's profile"""
        self.client.force_login(self.user)

        data = json.dumps({"profile": {"bio": "abc123"}})
        response = self.client.put(
            f'/users/{self.user.username}/?expand=profile', data=data, content_type="application/json"
        )

        body = response.json()
        self.assertEqual(200, response.status_code)
        self.assertEqual(body['profile']['bio'], 'abc123')
        self.assertEqual(body['username'], self.user.username)

    def test_cannot_update_external_profile(self):
        """We should not be able to update another user's profile"""
        self.client.force_login(self.user)

        data = json.dumps({"profile": {"bio": "abc123"}})
        response = self.client.put(
            f'/users/{self.other.username}/?expand=profile', data=data, content_type="application/json"
        )

        self.assertEqual(403, response.status_code)

    def test_update_other_profile_fails(self):
        """We should not be able to update a user's profile"""
        self.client.force_login(self.other)

        data = json.dumps({"profile": {"bio": "abc123"}})
        response = self.client.put(
            f'/users/{self.user.username}/?expand=profile', data=data, content_type="application/json"
        )

        self.assertEqual(403, response.status_code)


class FollowViewTestCase(AuthTestCase):

    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(username='me', email='me@example.com')
        self.other = get_user_model().objects.create_user(username='other', email='other@example.com')

    def test_cannot_delete_account(self):
        """A user should not be able to delete their account"""
        self.client.force_login(self.user)
        response = self.client.delete(f'/users/{self.user.username}/')
        self.assertEqual(405, response.status_code)

    def test_get_returns_follow_list(self):
        """All follows are returned"""
        self.client.force_login(self.user)
        Follow.objects.create(follower=self.other, followee=self.user)

        response = self.client.get(f'/users/{self.user.username}/follows/')
        self.assertEqual(200, response.status_code)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]['id'], self.other.id)

    def test_get_returns_individual_follow(self):
        """Can filter to an individual follow"""
        self.client.force_login(self.user)
        third_user = get_user_model().objects.create_user(username='hii', email='hii@example.com')

        Follow.objects.create(follower=self.other, followee=self.user)
        Follow.objects.create(follower=third_user, followee=self.user)

        response = self.client.get(f'/users/{self.user.username}/follows/?username={self.other.username}')
        self.assertEqual(200, response.status_code)
        body = response.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]['id'], self.other.id)

    def test_get_returns_filtered_follow_list(self):
        """Can filter to a list of follows"""
        self.client.force_login(self.user)
        third_user = get_user_model().objects.create_user(username='hii', email='hii@example.com')

        Follow.objects.create(follower=self.other, followee=self.user)
        Follow.objects.create(follower=third_user, followee=self.user)

        response = self.client.get(
            f'/users/{self.user.username}/follows/?username__in={self.other.username},{third_user.username}'
        )
        self.assertEqual(200, response.status_code)
        body = response.json()
        self.assertEqual(len(body), 2)

    def test_get_invalid_username_fails(self):
        """Getting an invalid username fails"""
        self.client.force_login(self.user)
        Follow.objects.create(follower=self.other, followee=self.user)

        response = self.client.get(f'/users/whatever/follows/')
        self.assertEqual(404, response.status_code)
        body = response.json()
        self.assertEqual(body['status'], 'error')
        self.assertEqual(body['type'], 'unknown-username')

    def test_put_can_add_follow(self):
        """It is possible to add a follow"""
        self.client.force_login(self.user)

        response = self.client.put(
            f'/users/{self.user.username}/follows/',
            data=json.dumps({'username': self.other.username}),
            content_type='application/json'
        )
        self.assertEqual(200, response.status_code)

        follow = Follow.objects.filter(follower=self.user, followee=self.other).first()
        self.assertIsNotNone(follow)

    def test_put_cannot_add_follow_for_other_user(self):
        """It is not possible to force a follow for another user"""
        self.client.force_login(self.user)

        response = self.client.put(
            f'/users/{self.other.username}/follows/',
            data=json.dumps({'username': self.user.username}),
            content_type='application/json'
        )
        self.assertEqual(403, response.status_code)

    def test_put_invalid_username_fails(self):
        """Requesting an invalid username path fails"""
        self.client.force_login(self.user)

        response = self.client.put(
            f'/users/whatever/follows/',
            data=json.dumps({'username': self.other.username}),
            content_type='application/json'
        )

        self.assertEqual(403, response.status_code)

    def test_put_invalid_target_username_fails(self):
        """Requesting to follow an invalid username fails"""
        self.client.force_login(self.user)

        response = self.client.put(
            f'/users/{self.user.username}/follows/',
            data=json.dumps({'username': 'whatever'}),
            content_type='application/json'
        )

        self.assertEqual(404, response.status_code)

    def test_put_missing_target_username_fails(self):
        """Requesting to follow without a username fails"""
        self.client.force_login(self.user)

        response = self.client.put(
            f'/users/{self.user.username}/follows/',
            content_type='application/json'
        )

        self.assertEqual(400, response.status_code)
        body = response.json()
        self.assertEqual(body['status'], 'error')
        self.assertEqual(body['type'], 'missing-fields')

    def test_put_add_follow_idempotent(self):
        """If you're already following someone, doing it again doesn't affect anything"""
        self.client.force_login(self.user)

        response = self.client.put(
            f'/users/{self.user.username}/follows/',
            data=json.dumps({'username': self.other.username}),
            content_type='application/json'
        )
        response = self.client.put(
            f'/users/{self.user.username}/follows/',
            data=json.dumps({'username': self.other.username}),
            content_type='application/json'
        )
        self.assertEqual(200, response.status_code)
        count = Follow.objects.filter(follower=self.user, followee=self.other).count()
        self.assertEqual(1, count)

    def test_delete_removes_follow(self):
        """If you delete a follow it deletes the model object"""
        self.client.force_login(self.user)

        Follow.objects.create(follower=self.user, followee=self.other)

        response = self.client.delete(
            f'/users/{self.user.username}/follows/',
            data=json.dumps({'username': self.other.username}),
            content_type='application/json'
        )
        self.assertEqual(204, response.status_code)
        count = Follow.objects.filter(follower=self.user, followee=self.other).count()
        self.assertEqual(0, count)

    def test_delete_invalid_username_fails(self):
        """Deleting an invalid username path fails"""
        self.client.force_login(self.user)

        response = self.client.delete(
            f'/users/whatever/follows/',
            data=json.dumps({'username': self.other.username}),
            content_type='application/json'
        )

        self.assertEqual(403, response.status_code)

    def test_delete_invalid_target_username_fails(self):
        """Requesting to delete an invalid username fails"""
        self.client.force_login(self.user)

        response = self.client.delete(
            f'/users/{self.user.username}/follows/',
            data=json.dumps({'username': 'whatever'}),
            content_type='application/json'
        )

        self.assertEqual(404, response.status_code)
        body = response.json()
        self.assertEqual(body['status'], 'error')
        self.assertEqual(body['type'], 'unknown-username')

    def test_delete_missing_target_username_fails(self):
        """Requesting to delete without a username fails"""
        self.client.force_login(self.user)

        response = self.client.delete(
            f'/users/{self.user.username}/follows/',
            content_type='application/json'
        )

        self.assertEqual(400, response.status_code)
        body = response.json()
        self.assertEqual(body['status'], 'error')
        self.assertEqual(body['type'], 'missing-fields')

    def test_delete_idempotent(self):
        """Deleting a follow is idempotent"""
        self.client.force_login(self.user)

        Follow.objects.create(follower=self.user, followee=self.other)

        response = self.client.delete(
            f'/users/{self.user.username}/follows/',
            data=json.dumps({'username': self.other.username}),
            content_type='application/json'
        )
        response = self.client.delete(
            f'/users/{self.user.username}/follows/',
            data=json.dumps({'username': self.other.username}),
            content_type='application/json'
        )
        self.assertEqual(204, response.status_code)
        count = Follow.objects.filter(follower=self.user, followee=self.other).count()
        self.assertEqual(0, count)

    def test_first_add_sends_target_email(self):
        self.client.force_login(self.user)
        response = self.client.put(
            f'/users/{self.user.username}/follows/',
            data=json.dumps({'username': self.other.username}),
            content_type='application/json'
        )

        self.assertEqual(200, response.status_code)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user.username, str(mail.outbox[0].message().get_payload(0)))
        self.assertIn(self.user.username, str(mail.outbox[0].message().get_payload(1)))
