from posts.settings.base import *  # noqa: F401 F403

DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

IS_HTTPS = False