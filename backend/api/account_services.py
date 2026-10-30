import secrets
from datetime import timedelta

from django.contrib.auth.hashers import check_password, make_password
from django.db import transaction
from django.utils import timezone

from .models import AccountProfile, OTPChallenge
from .otp_delivery import deliver_otp


OTP_LIFETIME = timedelta(minutes=5)
OTP_RESEND_COOLDOWN = timedelta(seconds=60)
OTP_MAX_ATTEMPTS = 5


class OTPError(Exception):
    pass


@transaction.atomic
def issue_challenge(user, channel, purpose, existing=None):
    now = timezone.now()
    if existing is None:
        existing = (
            OTPChallenge.objects.filter(
                user=user,
                channel=channel,
                purpose=purpose,
                consumed_at__isnull=True,
            )
            .order_by("-created_at")
            .first()
        )
    if existing and existing.sent_at + OTP_RESEND_COOLDOWN > now:
        raise OTPError("Please wait before requesting another code.")

    code = f"{secrets.randbelow(1_000_000):06d}"
    if existing:
        challenge = existing
        challenge.code_hash = make_password(code)
        challenge.created_at = now
        challenge.sent_at = now
        challenge.expires_at = now + OTP_LIFETIME
        challenge.attempts = 0
        challenge.verified_at = None
        challenge.consumed_at = None
        challenge.save(
            update_fields=(
                "code_hash",
                "created_at",
                "sent_at",
                "expires_at",
                "attempts",
                "verified_at",
                "consumed_at",
            )
        )
    else:
        OTPChallenge.objects.filter(
            user=user,
            channel=channel,
            purpose=purpose,
            consumed_at__isnull=True,
        ).update(consumed_at=now)
        challenge = OTPChallenge.objects.create(
            user=user,
            channel=channel,
            purpose=purpose,
            code_hash=make_password(code),
            sent_at=now,
            expires_at=now + OTP_LIFETIME,
        )

    profile = AccountProfile.objects.get(user=user)
    recipient = profile.email_key if channel == OTPChallenge.Channel.EMAIL else profile.mobile_number
    deliver_otp(channel, recipient, code, purpose)
    return challenge


def verify_challenge(challenge_id, code, purpose, channel=None):
    now = timezone.now()
    error_message = None
    verified = None
    with transaction.atomic():
        try:
            challenge = (
                OTPChallenge.objects.select_for_update()
                .select_related("user")
                .get(pk=challenge_id, purpose=purpose)
            )
        except (OTPChallenge.DoesNotExist, ValueError):
            raise OTPError("The verification code is invalid or expired.")

        if channel and challenge.channel != channel:
            raise OTPError("The verification code is invalid or expired.")
        if challenge.channel != OTPChallenge.Channel.EMAIL:
            raise OTPError("The verification code is invalid or expired.")
        if challenge.consumed_at or challenge.verified_at:
            raise OTPError("The verification code is invalid or expired.")
        if challenge.expires_at <= now or challenge.attempts >= OTP_MAX_ATTEMPTS:
            challenge.consumed_at = now
            challenge.save(update_fields=("consumed_at",))
            error_message = "The verification code is invalid or expired."
        elif not check_password(code, challenge.code_hash):
            challenge.attempts += 1
            challenge.save(update_fields=("attempts",))
            error_message = "The verification code is invalid or expired."
        else:
            challenge.verified_at = now
            challenge.save(update_fields=("verified_at",))
            if purpose == OTPChallenge.Purpose.REGISTRATION:
                profile = AccountProfile.objects.select_for_update().get(
                    user=challenge.user
                )
                profile.email_verified = True
                profile.save(update_fields=("email_verified", "updated_at"))
                challenge.consumed_at = now
                challenge.save(update_fields=("consumed_at",))
                challenge.user.is_active = True
                challenge.user.save(update_fields=("is_active",))
            verified = challenge
    if error_message:
        raise OTPError(error_message)
    return verified
