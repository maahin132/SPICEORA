import re
import time
import uuid

import phonenumbers
from django.contrib.auth import get_user_model, login, logout, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.core.validators import EmailValidator
from django.middleware.csrf import get_token
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .account_services import OTPError, issue_challenge, verify_challenge
from .auth_throttles import AccountThrottle
from .models import AccountProfile, OTPChallenge
from .otp_delivery import DeliveryUnavailable, provider_configured


User = get_user_model()
OTP_RE = re.compile(r"^[0-9]{6}$")
REGISTRATION_MIN_RESPONSE_SECONDS = 1.0
REGISTRATION_MESSAGE = (
    "If the details are eligible, check your email for verification instructions. "
    "Your mobile number remains unverified."
)


def invalid_fields(errors, status=400):
    return Response({"errors": errors}, status=status)


def registration_acknowledgement(challenge_id, started_at):
    remaining = REGISTRATION_MIN_RESPONSE_SECONDS - (time.perf_counter() - started_at)
    if remaining > 0:
        time.sleep(remaining)
    return Response(
        {
            "challenge_id": str(challenge_id),
            "email_verified": False,
            "mobile_verified": False,
            "message": REGISTRATION_MESSAGE,
        },
        status=201,
    )


def normalize_phone(value):
    try:
        parsed = phonenumbers.parse(value, None)
    except phonenumbers.NumberParseException:
        raise ValueError("Enter a valid mobile number with country code.")
    if not phonenumbers.is_valid_number(parsed):
        raise ValueError("Enter a valid mobile number with country code.")
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)


def validate_otp_body(data):
    challenge_id = data.get("challenge_id")
    code = data.get("code")
    if not challenge_id or not code or not OTP_RE.fullmatch(str(code)):
        return None, invalid_fields(
            {"code": ["Enter the six-digit verification code."]}
        )
    try:
        return uuid.UUID(str(challenge_id)), None
    except (ValueError, TypeError):
        return None, invalid_fields(
            {"code": ["The verification code is invalid or expired."]}
        )


def account_payload(user):
    profile = getattr(user, "account_profile", None)
    permissions = sorted(user.get_all_permissions()) if user.is_staff else []
    return {
        "id": user.pk,
        "role": "staff" if user.is_staff else "customer",
        "full_name": profile.full_name if profile else user.get_full_name(),
        "email": profile.email_key if profile else user.email,
        "mobile_number": profile.mobile_number if profile else None,
        "mobile_verified": profile.mobile_verified if profile else None,
        "permissions": permissions,
    }


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CSRFInitializationView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def get(self, request):
        return Response({"csrf_token": get_token(request)})


@method_decorator(csrf_protect, name="dispatch")
class RegistrationView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle, AccountThrottle)
    throttle_scope = "auth_registration"

    def post(self, request):
        started_at = time.perf_counter()
        data = request.data
        allowed = {"full_name", "email", "mobile_number", "password", "confirm_password"}
        errors = {
            key: ["Unknown field."]
            for key in sorted(set(data) - allowed)
        } if isinstance(data, dict) else {"non_field_errors": ["Submit a JSON object."]}
        if errors:
            return invalid_fields(errors)

        full_name = str(data.get("full_name", "")).strip()
        email = str(data.get("email", "")).strip().lower()
        mobile = str(data.get("mobile_number", "")).strip()
        password = data.get("password", "")
        confirm_password = data.get("confirm_password", "")
        if not full_name or len(full_name) > 160:
            errors["full_name"] = ["Enter your full name."]
        try:
            EmailValidator()(email)
        except DjangoValidationError:
            errors["email"] = ["Enter a valid email address."]
        try:
            mobile = normalize_phone(mobile)
        except ValueError as error:
            errors["mobile_number"] = [str(error)]
        if not isinstance(password, str) or not password:
            errors["password"] = ["Enter a password."]
        elif password != confirm_password:
            errors["confirm_password"] = ["Passwords do not match."]
        if errors:
            return invalid_fields(errors)
        try:
            password_validation.validate_password(
                password,
                User(username=email, email=email),
            )
        except DjangoValidationError as error:
            return invalid_fields({"password": list(error.messages)})

        if (
            AccountProfile.objects.filter(email_key__iexact=email).exists()
            or User.objects.filter(email__iexact=email).exists()
            or AccountProfile.objects.filter(mobile_number=mobile).exists()
        ):
            return registration_acknowledgement(uuid.uuid4(), started_at)

        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=uuid.uuid4().hex,
                    email=email,
                    password=password,
                    is_active=False,
                )
                AccountProfile.objects.create(
                    user=user,
                    full_name=full_name,
                    email_key=email,
                    mobile_number=mobile,
                )
                challenge = issue_challenge(
                    user,
                    OTPChallenge.Channel.EMAIL,
                    OTPChallenge.Purpose.REGISTRATION,
                )
        except DeliveryUnavailable:
            return registration_acknowledgement(uuid.uuid4(), started_at)
        except IntegrityError:
            if (
                AccountProfile.objects.filter(email_key__iexact=email).exists()
                or User.objects.filter(email__iexact=email).exists()
                or AccountProfile.objects.filter(mobile_number=mobile).exists()
            ):
                return registration_acknowledgement(uuid.uuid4(), started_at)
            return Response(
                {"message": "Registration could not be completed. Please try again later."},
                status=503,
            )

        return registration_acknowledgement(challenge.pk, started_at)


@method_decorator(csrf_protect, name="dispatch")
class RegistrationVerificationView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle, AccountThrottle)
    throttle_scope = "auth_otp"
    channel = None

    def post(self, request):
        challenge_id, error_response = validate_otp_body(request.data)
        if error_response:
            return error_response
        try:
            challenge = verify_challenge(
                challenge_id,
                str(request.data["code"]),
                OTPChallenge.Purpose.REGISTRATION,
                self.channel,
            )
        except OTPError as error:
            return invalid_fields({"code": [str(error)]}, status=400)
        profile = challenge.user.account_profile
        return Response(
            {
                "email_verified": profile.email_verified,
                "mobile_verified": profile.mobile_verified,
                "account_active": challenge.user.is_active,
                "message": (
                    "Your email is verified and your account is active."
                    if challenge.user.is_active
                    else "Email verification is not complete."
                ),
            }
        )


class VerifyEmailView(RegistrationVerificationView):
    channel = OTPChallenge.Channel.EMAIL


class VerifyMobileView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request):
        return Response(
            {"message": "Mobile verification is not available yet."},
            status=410,
        )


@method_decorator(csrf_protect, name="dispatch")
class ResendRegistrationOTPView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle, AccountThrottle)
    throttle_scope = "auth_otp"

    def post(self, request):
        challenge_id = request.data.get("challenge_id")
        try:
            challenge = OTPChallenge.objects.select_related("user").get(
                pk=challenge_id,
                channel=OTPChallenge.Channel.EMAIL,
                purpose=OTPChallenge.Purpose.REGISTRATION,
                consumed_at__isnull=True,
                user__is_active=False,
            )
        except (OTPChallenge.DoesNotExist, ValueError, TypeError):
            return invalid_fields(
                {"challenge_id": ["The verification request is invalid or expired."]},
                status=400,
            )
        try:
            issue_challenge(
                challenge.user,
                challenge.channel,
                challenge.purpose,
                existing=challenge,
            )
        except OTPError as error:
            return invalid_fields({"resend": [str(error)]}, status=429)
        except DeliveryUnavailable:
            return Response(
                {
                    "delivery": "unavailable",
                    "message": "Verification delivery is unavailable. Try again later.",
                },
                status=503,
            )
        return Response({"delivery": "sent", "message": "A new code was sent."})


@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle, AccountThrottle)
    throttle_scope = "auth_login"
    audience = "customer"

    def post(self, request):
        if not isinstance(request.data, dict):
            return invalid_fields({"non_field_errors": ["Submit a JSON object."]})
        identity = str(request.data.get("identity", "")).strip()
        password = request.data.get("password")
        if not identity or not isinstance(password, str):
            return Response(
                {"message": "The credentials are invalid or the account is not verified."},
                status=401,
            )
        profile = AccountProfile.objects.select_related("user").filter(
            email_key__iexact=identity.lower()
        ).first()
        user = profile.user if profile else None
        if self.audience == "staff" and user is None:
            user = User.objects.filter(email__iexact=identity, is_staff=True).first()
        valid = bool(user and user.check_password(password) and user.is_active)
        if self.audience == "customer":
            valid = bool(
                valid
                and profile
                and not user.is_staff
                and profile.email_verified
            )
        else:
            valid = bool(valid and user.is_staff)
        if not valid:
            return Response(
                {"message": "The credentials are invalid or the account is not verified."},
                status=401,
            )
        login(request, user)
        return Response(
            {"user": account_payload(user), "csrf_token": get_token(request)}
        )


class OperationsLoginView(LoginView):
    audience = "staff"


class CurrentAccountView(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (AllowAny,)

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return Response({"user": None})
        if user.is_staff:
            return Response({"user": account_payload(user)})
        try:
            profile = user.account_profile
        except AccountProfile.DoesNotExist:
            return Response({"user": None}, status=401)
        if not (user.is_active and profile.email_verified):
            return Response({"user": None}, status=401)
        return Response({"user": account_payload(user)})


@method_decorator(csrf_protect, name="dispatch")
class LogoutView(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        logout(request)
        return Response({"message": "You have been signed out."})


@method_decorator(csrf_protect, name="dispatch")
class PasswordRecoveryStartView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle, AccountThrottle)
    throttle_scope = "auth_recovery"

    def post(self, request):
        if not isinstance(request.data, dict):
            return invalid_fields({"non_field_errors": ["Submit a JSON object."]})
        identity = str(request.data.get("identity", "")).strip()
        channel = request.data.get("channel", OTPChallenge.Channel.EMAIL)
        flow_id = uuid.uuid4()
        if channel != OTPChallenge.Channel.EMAIL:
            return invalid_fields(
                {"channel": ["Email recovery is currently the only available option."]}
            )
        profile = None
        if identity:
            profile = AccountProfile.objects.select_related("user").filter(
                email_key__iexact=identity.lower()
            ).first()
        if (
            profile
            and profile.user.is_active
            and profile.email_verified
        ):
            try:
                challenge = issue_challenge(
                    profile.user,
                    OTPChallenge.Channel.EMAIL,
                    OTPChallenge.Purpose.PASSWORD_RESET,
                )
                flow_id = challenge.pk
            except (DeliveryUnavailable, OTPError):
                pass
        return Response(
            {
                "flow_id": str(flow_id),
                "message": "If the details match an active customer account, verification instructions will be sent.",
            },
            status=202,
        )


@method_decorator(csrf_protect, name="dispatch")
class PasswordRecoveryVerifyView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle, AccountThrottle)
    throttle_scope = "auth_otp"

    def post(self, request):
        challenge_id, error_response = validate_otp_body(request.data)
        if error_response:
            return error_response
        try:
            challenge = verify_challenge(
                challenge_id,
                str(request.data["code"]),
                OTPChallenge.Purpose.PASSWORD_RESET,
                OTPChallenge.Channel.EMAIL,
            )
        except OTPError as error:
            return invalid_fields({"code": [str(error)]}, status=400)
        return Response(
            {"flow_id": str(challenge.pk), "verified": True}
        )


@method_decorator(csrf_protect, name="dispatch")
class PasswordRecoveryResetView(APIView):
    authentication_classes = ()
    permission_classes = (AllowAny,)
    throttle_classes = (ScopedRateThrottle, AccountThrottle)
    throttle_scope = "auth_recovery"

    def post(self, request):
        flow_id = request.data.get("flow_id")
        password = request.data.get("password")
        confirmation = request.data.get("confirm_password")
        if not isinstance(password, str) or not password or password != confirmation:
            return invalid_fields(
                {"confirm_password": ["Enter matching new passwords."]}
            )
        try:
            flow_id = uuid.UUID(str(flow_id))
        except (ValueError, TypeError):
            return invalid_fields(
                {"flow_id": ["Verify a recovery code before resetting the password."]},
                status=400,
            )
        with transaction.atomic():
            try:
                challenge = (
                    OTPChallenge.objects.select_for_update()
                    .select_related("user")
                    .get(
                        pk=flow_id,
                        purpose=OTPChallenge.Purpose.PASSWORD_RESET,
                        channel=OTPChallenge.Channel.EMAIL,
                        verified_at__isnull=False,
                        consumed_at__isnull=True,
                    )
                )
            except OTPChallenge.DoesNotExist:
                return invalid_fields(
                    {"flow_id": ["Verify a recovery code before resetting the password."]},
                    status=400,
                )
            if challenge.expires_at <= timezone.now():
                return invalid_fields(
                    {"flow_id": ["The recovery verification has expired."]},
                    status=400,
                )
            try:
                password_validation.validate_password(password, challenge.user)
            except DjangoValidationError as error:
                return invalid_fields({"password": list(error.messages)})
            challenge.user.set_password(password)
            challenge.user.save(update_fields=("password",))
            challenge.consumed_at = timezone.now()
            challenge.save(update_fields=("consumed_at",))
            invalidate_user_sessions(challenge.user.pk)
        logout(request)
        return Response({"message": "Your password was reset. Sign in with your new password."})


def invalidate_user_sessions(user_id):
    from django.contrib.sessions.models import Session

    user_key = str(user_id)
    for session in Session.objects.filter(expire_date__gt=timezone.now()).iterator():
        if session.get_decoded().get("_auth_user_id") == user_key:
            session.delete()


class ProviderHealthView(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAdminUser,)

    def get(self, request):
        return Response(
            {
                "email_configured": provider_configured(OTPChallenge.Channel.EMAIL),
                "sms_configured": provider_configured(OTPChallenge.Channel.SMS),
            }
        )
