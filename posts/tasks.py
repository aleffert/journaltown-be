import os

from django.core.mail import send_mail
from django.template import loader
from django.contrib.auth.models import User

from posts.email import login
from posts import models


def send_registration_verification_email(token: models.EmailVerificationToken):
    email_subject = "Welcome to JournalTown"
    email_plaintext = """
To register, just follow this link: {protocol}://{web_origin}/?token={callback_token}
Enjoy,
- The JournalTown Team
    """
    email_html = 'registration_verification_email.html'

    context = {'callback_token': token.token, **login.link_context()}
    html_message = loader.render_to_string(email_html, context)
    send_mail(
        email_subject,
        email_plaintext.format(**context),
        os.getenv('PASSWORDLESS_EMAIL_NOREPLY_ADDRESS'),
        [token.email],
        fail_silently=False,
        html_message=html_message
    )


def send_follow_email(follow: models.Follow, target: User):
    username = follow.follower.username
    email_subject = f"New follower on JournalTown!"
    email_plaintext = """
Guess what? {username} just followed you on JournalTown.
Check out their profile: {protocol}://{web_origin}/u/{username}/profile
or see their posts: {protocol}://{web_origin}/u/{username}/
Enjoy,
- The JournalTown Team
    """
    email_html = 'new_follower_email.html'

    context = {'username': username, **login.link_context()}
    html_message = loader.render_to_string(email_html, context)
    send_mail(
        email_subject,
        email_plaintext.format(**context),
        os.getenv('PASSWORDLESS_EMAIL_NOREPLY_ADDRESS'),
        [target.email],
        fail_silently=False,
        html_message=html_message
    )
