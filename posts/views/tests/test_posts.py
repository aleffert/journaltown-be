import json
from django.contrib.auth import get_user_model

from posts.tests.utils import AuthTestCase


class CurrentUserViewTest(AuthTestCase):

    def setUp(self):
        super().setUp()
        self.user = get_user_model().objects.create_user(username='me', email='me@example.com')
        self.other_user = get_user_model().objects.create_user(username='other', email='other@example.com')

    def test_not_logged_in_returns_unauthorized(self):
        """If a user is not logged in, the request should fail"""
        response = self.client.get('/posts/')
        self.assertEqual(401, response.status_code)

    def test_no_posts_returns_empty_list(self):
        """If there are no posts we should get an empty list"""
        self.client.force_login(self.user)
        response = self.client.get('/posts/')
        self.assertEqual(200, response.status_code)
        self.assertEqual([], response.json())

    def test_post_creates_post(self):
        """We should be able to create a new post"""
        self.client.force_login(self.user)

        # create
        payload = {'title': 'title', 'body': 'stuff'}
        response = self.client.post('/posts/', data=json.dumps(payload), content_type='application/json')
        body = response.json()

        # verify
        self.assertEqual(201, response.status_code)
        self.assertEqual(set(body.keys()), set(['id', 'author', 'created_at', 'title', 'body', 'last_modified']))
        self.assertEqual(body['author'], self.user.pk)
        self.assertEqual(body['title'], payload['title'])
        self.assertEqual(body['body'], payload['body'])
        self.assertIsNotNone(body['created_at'])
        self.assertIsNotNone(body['last_modified'])

    def test_can_update_content(self):
        """We should be able to update a new post"""
        self.client.force_login(self.user)

        # create
        payload = {'title': 'title', 'body': 'stuff'}
        response = self.client.post('/posts/', data=json.dumps(payload), content_type='application/json', accept='application/json')
        body = response.json()

        # update
        payload = {'title': 'title2', 'body': 'stuff2'}
        response = self.client.put(f"/posts/{body['id']}/", data=json.dumps(payload), content_type='application/json')
        body = response.json()

        # verify
        self.assertEqual(200, response.status_code)
        self.assertEqual(body['title'], payload['title'])
        self.assertEqual(body['body'], payload['body'])

    def test_cannot_update_author(self):
        """Once a post is created its author can't be changed by updating the object"""

        self.client.force_login(self.user)
        payload = {'title': 'title', 'body': 'stuff'}
        response = self.client.post('/posts/', data=json.dumps(payload), content_type='application/json', accept='application/json')
        body = response.json()

        payload = {'author': str(self.other_user.pk)}
        response = self.client.put(f"/posts/{body['id']}/", data=json.dumps(payload), content_type='application/json')
        body = response.json()
        self.assertEqual(200, response.status_code)
        self.assertEqual(body['author'], self.user.pk)