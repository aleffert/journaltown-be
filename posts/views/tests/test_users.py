from django.contrib.auth import get_user_model

from posts.tests.utils import AuthTestCase


class CurrentUserViewTest(AuthTestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(username='me', email='me@example.com')

    def test_not_logged_in_returns_unauthorized(self):
        response = self.client.get('/me/')
        self.assertEqual(401, response.status_code)

    def test_logged_in_returns_user_info(self):
        self.client.force_login(self.user)
        response = self.client.get('/me/')
        self.assertEqual(200, response.status_code)
        self.assertEqual({'username': 'me', 'email': 'me@example.com'}, response.json())
