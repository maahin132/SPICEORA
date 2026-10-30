import smtplib

from django.conf import settings
from django.core.mail import EmailMessage
from django.core.mail.message import BadHeaderError

GOOGLE_SMTP_HOST = "smtp.gmail.com"


class DeliveryUnavailable(Exception):
    pass


def provider_configured(channel):
    if channel == "email":
        return bool(
            settings.EMAIL_PROVIDER == "gmail"
            and settings.EMAIL_HOST == GOOGLE_SMTP_HOST
            and settings.EMAIL_PORT == 587
            and settings.EMAIL_USE_TLS
            and not settings.EMAIL_USE_SSL
            and settings.EMAIL_HOST_USER
            and settings.EMAIL_HOST_PASSWORD
            and settings.DEFAULT_FROM_EMAIL
            and settings.DEFAULT_FROM_EMAIL.casefold()
            == settings.EMAIL_HOST_USER.casefold()
        )
    return False


def deliver_otp(channel, recipient, code, purpose):
    if channel != "email":
        raise DeliveryUnavailable("SMS verification is not available.")
    if not provider_configured(channel):
        raise DeliveryUnavailable("Email verification is not configured.")
    subject = (
        "SPICEORA account verification"
        if purpose == "registration"
        else "SPICEORA password recovery"
    )
    body = (
        f"Your SPICEORA verification code is {code}. "
        "It expires in five minutes. Do not share this code."
    )
    try:
        message = EmailMessage(
            subject=subject,
            body=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient],
            connection=None,
        )
        if message.send(fail_silently=False) != 1:
            raise DeliveryUnavailable("Email delivery did not complete.")
    except DeliveryUnavailable:
        raise
    except (smtplib.SMTPException, OSError, BadHeaderError, UnicodeError) as error:
        raise DeliveryUnavailable("Verification delivery failed.") from error
