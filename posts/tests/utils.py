from django.test.client import Client
from django.test import TestCase
from rest_framework.authtoken.models import Token


class TokenAuthClient(Client):

    token = None

    def force_login(self, user):
        (token, _) = Token.objects.get_or_create(user=user)
        self.token = token.key

    def request(self, **request):
        if(self.token):
            return super().request(**request, HTTP_AUTHORIZATION=f'Token {self.token}')
        else:
            return super().request(**request)


class AuthTestCase(TestCase):
    client_class = TokenAuthClient
