import json
from django.contrib.auth import get_user_model

from posts.tests.utils import AuthTestCase


class CurrentUserViewTest(AuthTestCase):

    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(username='me', email='me@example.com')

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

    def test_update_profile(self):
        """We should just be able to update a user's profile"""
        self.client.force_login(self.user)

        data = json.dumps({"profile": {"bio": "abc123"}})
        response = self.client.put(f'/users/{self.user.username}/?expand=profile', data=data, content_type="application/json")

        body = response.json()
        self.assertEqual(200, response.status_code)
        self.assertEqual(body['profile']['bio'], 'abc123')
        self.assertEqual(body['username'], self.user.username)
