from django.contrib.auth import get_user_model
from posts import errors


class UsernameScopedMixin:

    def get_user_or_404(self, username, check=True):
        if not username:
            raise errors.ResponseException(errors.MissingFieldsError(['username']), 400)

        user = get_user_model().objects.filter(username=username).first()
        if not user:
            raise errors.ResponseException(errors.InvalidUsernameError(username), 404)

        if check:
            self.check_object_permissions(self.request, user)

        return user
