import datetime
import json

from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.utils import timezone

from posts.models import EmailVerificationToken


class SendRegistrationVerificationViewTestCase(TestCase):

    def test_token_send_succeeds_for_unknown_email(self):
        """When we send a token the request returns success"""
        email = 'test@example.com'
        response = self.client.post(
            '/register/email/',
            data=json.dumps({'email': email}),
            content_type='application/json'
        )

        token = EmailVerificationToken.objects.filter(email=email).first()
        self.assertEqual(204, response.status_code)
        self.assertIsNotNone(token)

    def test_token_send_sends_email(self):
        """When we create a token it sends an email containing that token"""
        email = 'test@example.com'
        self.client.post(
            '/register/email/',
            data=json.dumps({'email': email}),
            content_type='application/json'
        )

        token = EmailVerificationToken.objects.filter(email=email).first()
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(token.token, mail.outbox[0].message().get_payload(0).as_string())
        self.assertIn(token.token, mail.outbox[0].message().get_payload(1).as_string())

    def test_token_success_erases_old_token(self):
        """If the token is created any old tokens should be invalidated"""
        email = 'test@example.com'
        token = EmailVerificationToken.objects.create(email=email)
        old_key = token.token
        self.client.post(
            '/register/email/',
            data=json.dumps({'email': email}),
            content_type='application/json'
        )

        token = EmailVerificationToken.objects.filter(email=email).first()
        self.assertNotEqual(old_key, token.token)

    def test_token_send_fails_for_invalid_email(self):
        """If the email is invalid we should fail"""
        response = self.client.post(
            '/register/email/',
            data=json.dumps({'email': 'abc'}),
            content_type='application/json'
        )

        body = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual(body['status'], 'error')
        self.assertEqual(body['type'], 'invalid-fields')

    def test_token_send_fails_for_known_email(self):
        """If the email already has a user we should fail"""
        user = get_user_model().objects.create_user(username='example', email='test@example.com')
        response = self.client.post(
            '/register/email/',
            data=json.dumps({'email': user.email}),
            content_type='application/json'
        )
        body = response.json()

        self.assertEqual(400, response.status_code)
        self.assertEqual(body['status'], 'error')
        self.assertEqual(body['type'], 'email-in-use')

    def test_token_send_fails_with_missing_email(self):
        """If the email field is missing we should return an error"""
        response = self.client.post('/register/email/')
        body = response.json()
        self.assertEqual(400, response.status_code)
        self.assertEqual(body['status'], 'error')
        self.assertEqual(body['type'], 'missing-fields')


class RegisterUserViewTestCase(TestCase):

    def test_missing_token_fails(self):
        """If the token field is missing in the post body we should return an error"""
        response = self.client.post('/callback/register/', content_type="application/json")
        body = response.json()
        self.assertEqual(400, response.status_code)
        self.assertEqual(body['status'], 'error')
        self.assertEqual(body['type'], 'missing-fields')
        self.assertIn('token', map(lambda e: e['name'], body['errors']))

    def test_missing_username_fails(self):
        """If the username field is missing in the post body we should return an error"""
        response = self.client.post('/callback/register/', content_type="application/json")
        body = response.json()
        self.assertEqual(400, response.status_code)
        self.assertEqual(body['status'], 'error')
        self.assertEqual(body['type'], 'missing-fields')
        self.assertIn('username', map(lambda e: e['name'], body['errors']))

    def test_missing_token_record_fails(self):
        """If the token object we pass doesn't exist in the db we should return an error"""
        response = self.client.post(
            '/callback/register/',
            data=json.dumps({'token': '12345', 'username': 'new-user'}),
            content_type="application/json"
        )
        body = response.json()
        self.assertEqual(400, response.status_code)
        self.assertEqual(body['status'], 'error')
        self.assertEqual(body['type'], 'missing-fields')
        self.assertIn('token', map(lambda e: e['name'], body['errors']))

    def test_expired_token_record_fails(self):
        """If the token object we pass is old, we should return an error"""
        token = EmailVerificationToken.objects.create()
        token.created_at = timezone.now() - datetime.timedelta(days=2)
        token.save()

        response = self.client.post(
            '/callback/register/',
            data=json.dumps({'token': token.token, 'username': 'new-user'}),
            content_type="application/json"
        )
        body = response.json()
        self.assertEqual(400, response.status_code)
        self.assertEqual(body['status'], 'error')
        self.assertEqual(body['type'], 'invalid-fields')
        self.assertIn('token', map(lambda e: e['name'], body['errors']))

    def test_invalid_username_fails(self):
        """If the username doesn't validate then creation fails"""
        token = EmailVerificationToken.objects.create()
        response = self.client.post(
            '/callback/register/',
            data=json.dumps({'token': token.token, 'username': 'new user'}),
            content_type="application/json"
        )
        body = response.json()
        self.assertEqual(400, response.status_code)
        self.assertEqual(body['status'], 'error')
        self.assertEqual(body['type'], 'invalid-fields')
        self.assertIn('username', map(lambda e: e['name'], body['errors']))
        self.assertIsNotNone(EmailVerificationToken.objects.filter(token=token.token).first())

    def test_creates_user(self):
        """If the call succeeds, a new user is created"""
        token = EmailVerificationToken.objects.create(email='test@example.com')
        response = self.client.post(
            '/callback/register/',
            data=json.dumps({'token': token.token, 'username': 'newuser'}),
            content_type="application/json"
        )
        self.assertEqual(201, response.status_code)

        user = get_user_model().objects.filter(username='newuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
        self.assertIsNone(EmailVerificationToken.objects.filter(token=token.token).first())

    def test_returns_valid_auth_token(self):
        """If the call succeeds, a new user is created"""
        token = EmailVerificationToken.objects.create(email='test@example.com')
        response = self.client.post(
            '/callback/register/',
            data=json.dumps({'token': token.token, 'username': 'newuser'}),
            content_type="application/json"
        )
        body = response.json()

        auth_token = body['token']

        response = self.client.get('/me/', HTTP_AUTHORIZATION=f'Token {auth_token}')
        self.assertEqual(200, response.status_code)


class UsernameAvailableViewTestCase(TestCase):

    def test_invalid_username_returns_failure(self):
        """If the username is invalid for some reason, return failure"""
        get_user_model().objects.create_user(username='abc123', email='test@example.com')

        response = self.client.get(
            '/users/Abc123/available/'
        )

        self.assertEqual(400, response.status_code)

    def test_valid_username_returns_success(self):
        """If the username is valid, return a success code"""
        response = self.client.get(
            '/users/Abc123/available/'
        )

        self.assertEqual(204, response.status_code)
