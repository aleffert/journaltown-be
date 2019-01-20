from __future__ import unicode_literals
from builtins import str

from django.core.exceptions import ValidationError
from django.http import JsonResponse


class JsonExceptionMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        if isinstance(exception, ValidationError):
            return JsonResponse(
                {'error': 'validation error', 'info': str(exception.message)},
                status=400
            )
