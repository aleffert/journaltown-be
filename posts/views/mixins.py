from django.contrib.auth import get_user_model
from rest_framework.response import Response
from posts import errors


class UsernameScopedMixin:

    def get_user_or_404(self, username, check=True):
        if not username:
            raise errors.OfResponse(Response(errors.MissingFieldsError(['username']).render(), 400))

        user = get_user_model().objects.filter(username=username).first()
        if not user:
            raise errors.OfResponse(Response(errors.InvalidUsernameError(username).render(), 404))

        if check:
            self.check_object_permissions(self.request, user)

        return user
