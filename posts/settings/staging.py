import os

from posts.settings.base import *  # noqa: F401 F403

ANYMAIL = {
    "MAILGUN_API_KEY": os.getenv("MAILGUN_API_KEY"),
    "MAILGUN_SENDER_DOMAIN": os.getenv('MAIL_DOMAIN')
}

EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
