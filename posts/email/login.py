import os

from django.conf import settings


def link_context():
    return {
        'web_origin': os.getenv('WEB_ORIGIN'),
        'protocol': 'https' if settings.IS_HTTPS else 'http'
    }
