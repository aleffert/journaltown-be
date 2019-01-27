from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django_registration import validators


class UsernameValidator:

    def __init__(self):
        self.validators = [
            validators.CaseInsensitiveUnique(
                get_user_model(), 'username',
                'Invalid username: Already taken'
            ),
            validators.ReservedNameValidator(),
            validators.validate_confusables,
            UnicodeUsernameValidator()
        ]

    def __call__(self, value):
        for validator in self.validators:
            validator(value)
