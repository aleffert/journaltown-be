import datetime

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from validate_email import validate_email

from posts import errors
from posts.models import EmailVerificationToken
from posts.tasks import send_registration_verification_email
from posts.validators import UsernameValidator

EMAIL_TOKEN_EXPIRATION_SECONDS = 60 * 60  # one hour


@api_view(['POST'])
def send_token_email(request):
    email = request.data.get('email', None)
    if email is None:
        return Response(errors.MissingFieldsError(['email']).render(), status=400)

    if not validate_email(email):
        return Response(errors.InvalidFieldsError(['email']).render(), status=400)

    if get_user_model().objects.filter(email=email).first():
        return Response(errors.EmailInUseError().render(), status=400)

    EmailVerificationToken.objects.filter(email=email).delete()

    token = EmailVerificationToken.objects.create(email=email)

    send_registration_verification_email(token)

    return Response(status=204)


@api_view(['POST'])
def register_email_callback(request):
    username = request.data.get('username', None)
    token = request.data.get('token', None)

    missing_fields = []
    if not username:
        missing_fields.append('username')
    if not token:
        missing_fields.append('token')

    if len(missing_fields):
        return Response(errors.MissingFieldsError(missing_fields).render(), status=400)

    verification_token = EmailVerificationToken.objects.filter(token=token).first()
    if not verification_token:
        return Response(errors.MissingFieldsError(['token']).render(), status=400)
    if verification_token.created_at + datetime.timedelta(seconds=EMAIL_TOKEN_EXPIRATION_SECONDS) < timezone.now():
        return Response(errors.InvalidFieldsError(['token']).render(), status=400)

    try:
        UsernameValidator()(username)
        user = get_user_model().objects.create_user(username=username, email=verification_token.email)
        verification_token.delete()
    except ValidationError:
        return Response(errors.InvalidFieldsError(['username']).render(), status=400)

    auth_token, created = Token.objects.get_or_create(user=user)

    if created:
        # Initially set an unusable password if a user is created through this.
        user.set_unusable_password()
        user.save()

    if auth_token:
        # Return our key for consumption.
        return Response({'token': auth_token.key}, status=201)


@api_view(['GET'])
def is_available(request, username):

    try:
        UsernameValidator()(username)
    except ValidationError:
        return Response(errors.InvalidFieldsError(['username']).render(), status=400)

    return Response(status=204)
