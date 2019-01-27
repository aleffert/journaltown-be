import os

from django.core.mail import send_mail
from django.template import loader

from posts.email import login


def send_registration_verification_email(token):
    email_subject = "Welcome to JournalTown"
    email_plaintext = """
To register, just follow this link: {protocol}://{web_origin}/?token={callback_token}
Enjoy,
- The JournalTown Team
    """
    email_html = 'registration_verification_email.html'

    # Inject context if user specifies.
    context = {'callback_token': token.token, **login.link_context()}
    html_message = loader.render_to_string(email_html, context,)
    send_mail(
        email_subject,
        email_plaintext.format(**context),
        os.getenv('PASSWORDLESS_EMAIL_NOREPLY_ADDRESS'),
        [token.email],
        fail_silently=False,
        html_message=html_message,)
