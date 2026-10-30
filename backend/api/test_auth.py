from datetime import timedelta
import smtplib
import time
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.test import override_settings
from django.utils import timezone
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from .account_services import OTPError, issue_challenge, verify_challenge
from .models import AccountProfile, Farm, OTPChallenge
from .otp_delivery import DeliveryUnavailable, deliver_otp, provider_configured


PASSWORD = "Spiceora!OwnerPass987"
EMAIL = "buyer@example.com"
MOBILE = "+14155552671"


@override_settings(
    PASSWORD_HASHERS=["django.contrib.auth.hashers.MD5PasswordHasher"],
)
class AccountAuthenticationAPITests(APITestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient(enforce_csrf_checks=True)
        self.csrf_token = self.initialize_csrf()

    def initialize_csrf(self):
        response = self.client.get(reverse("auth-csrf"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("csrftoken", self.client.cookies)
        return response.data["csrf_token"]

    def post_json(self, url_name, payload, token=None):
        return self.client.post(
            reverse(url_name),
            payload,
            format="json",
            HTTP_X_CSRFTOKEN=token or self.csrf_token,
        )

    def register_customer(self, email=EMAIL, mobile=MOBILE):
        codes = {}

        def capture(channel, recipient, code, purpose):
            codes[channel] = code

        with patch("api.account_services.deliver_otp", side_effect=capture):
            response = self.post_json(
                "auth-register",
                {
                    "full_name": "Test Buyer",
                    "email": email,
                    "mobile_number": mobile,
                    "password": PASSWORD,
                    "confirm_password": PASSWORD,
                },
            )
        self.assertEqual(response.status_code, 201, response.data)
        self.assertNotIn("code", response.data)
        return response, codes

    def verify_customer(self, registration, codes):
        response = self.post_json(
            "auth-verify-email",
            {
                "challenge_id": registration.data["challenge_id"],
                "code": codes[OTPChallenge.Channel.EMAIL],
            },
        )
        self.assertEqual(response.status_code, 200, response.data)
        return response

    def create_verified_customer(self, email=EMAIL, mobile=MOBILE):
        user_model = get_user_model()
        user = user_model.objects.create_user(
            username=f"customer-{AccountProfile.objects.count()}",
            email=email,
            password=PASSWORD,
            is_active=True,
        )
        profile = AccountProfile.objects.create(
            user=user,
            full_name="Test Buyer",
            email_key=email.lower(),
            mobile_number=mobile,
            email_verified=True,
            mobile_verified=False,
        )
        return user, profile

    def test_registration_requires_csrf_and_never_grants_staff(self):
        client = APIClient(enforce_csrf_checks=True)
        response = client.post(
            reverse("auth-register"),
            {
                "full_name": "Test Buyer",
                "email": EMAIL,
                "mobile_number": MOBILE,
                "password": PASSWORD,
                "confirm_password": PASSWORD,
            },
            format="json",
        )
        self.assertEqual(response.status_code, 403)

        registration, codes = self.register_customer()
        self.assertTrue(codes[OTPChallenge.Channel.EMAIL])
        self.assertEqual(set(codes), {OTPChallenge.Channel.EMAIL})
        self.assertEqual(set(registration.data), {"challenge_id", "email_verified", "mobile_verified", "message"})
        user = get_user_model().objects.get(email=EMAIL)
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.account_profile.email_verified)
        self.assertFalse(user.account_profile.mobile_verified)
        self.assertNotIn("password", registration.data)
        self.assertNotIn("is_staff", registration.data)

    def test_email_verification_activates_account_and_mobile_remains_unverified(self):
        registration, codes = self.register_customer()
        email_result = self.verify_customer(registration, codes)
        user = get_user_model().objects.get(email=EMAIL)
        self.assertEqual(email_result.status_code, 200)
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.account_profile.email_verified)
        self.assertFalse(user.account_profile.mobile_verified)
        self.assertTrue(email_result.data["account_active"])
        self.assertFalse(email_result.data["mobile_verified"])
        mobile_result = self.post_json(
            "auth-verify-mobile",
            {"challenge_id": registration.data["challenge_id"], "code": "123456"},
        )
        self.assertEqual(mobile_result.status_code, 410)
        user.account_profile.refresh_from_db()
        self.assertFalse(user.account_profile.mobile_verified)
        self.assertEqual(
            self.post_json(
                "auth-verify-email",
                {
                    "challenge_id": registration.data["challenge_id"],
                    "code": codes[OTPChallenge.Channel.EMAIL],
                },
            ).status_code,
            400,
        )

    def test_registration_responses_do_not_disclose_duplicate_email_or_mobile(self):
        new_registration, _ = self.register_customer()
        with patch("api.account_services.deliver_otp") as delivery:
            duplicate_email = self.post_json(
                "auth-register",
                {
                    "full_name": "Another Buyer",
                    "email": EMAIL.upper(),
                    "mobile_number": "+14155552672",
                    "password": PASSWORD,
                    "confirm_password": PASSWORD,
                },
            )
            duplicate_mobile = self.post_json(
                "auth-register",
                {
                    "full_name": "Another Buyer",
                    "email": "other@example.com",
                    "mobile_number": MOBILE,
                    "password": PASSWORD,
                    "confirm_password": PASSWORD,
                },
            )

        self.assertEqual(duplicate_email.status_code, new_registration.status_code)
        self.assertEqual(duplicate_mobile.status_code, new_registration.status_code)
        self.assertEqual(delivery.call_count, 0)
        self.assertEqual(
            set(duplicate_email.data),
            {"challenge_id", "email_verified", "mobile_verified", "message"},
        )
        self.assertEqual(
            set(duplicate_mobile.data),
            {"challenge_id", "email_verified", "mobile_verified", "message"},
        )
        for duplicate in (duplicate_email, duplicate_mobile):
            self.assertEqual(duplicate.data["email_verified"], False)
            self.assertEqual(duplicate.data["mobile_verified"], False)
            self.assertEqual(
                {
                    key: value
                    for key, value in duplicate.data.items()
                    if key != "challenge_id"
                },
                {
                    key: value
                    for key, value in new_registration.data.items()
                    if key != "challenge_id"
                },
            )
            self.assertFalse(
                OTPChallenge.objects.filter(pk=duplicate.data["challenge_id"]).exists()
            )

        self.assertEqual(get_user_model().objects.count(), 1)
        self.assertEqual(AccountProfile.objects.count(), 1)
        self.assertEqual(OTPChallenge.objects.count(), 1)

    def test_duplicate_and_new_registration_have_minimum_response_time(self):
        payload = {
            "full_name": "Test Buyer",
            "email": EMAIL,
            "mobile_number": MOBILE,
            "password": PASSWORD,
            "confirm_password": PASSWORD,
        }
        with (
            patch("api.account_services.deliver_otp"),
            patch("api.auth_views.REGISTRATION_MIN_RESPONSE_SECONDS", 0.05),
        ):
            start = time.perf_counter()
            new_registration = self.post_json("auth-register", payload)
            new_elapsed = time.perf_counter() - start

            duplicate_payload = {
                **payload,
                "mobile_number": "+14155552672",
            }
            start = time.perf_counter()
            duplicate_registration = self.post_json(
                "auth-register", duplicate_payload
            )
            duplicate_elapsed = time.perf_counter() - start

        self.assertEqual(new_registration.status_code, duplicate_registration.status_code)
        self.assertGreaterEqual(new_elapsed, 0.045)
        self.assertGreaterEqual(duplicate_elapsed, 0.045)
        self.assertLess(abs(new_elapsed - duplicate_elapsed), 0.5)

    def test_phone_number_must_be_valid_and_include_country_code(self):
        response = self.post_json(
            "auth-register",
            {
                "full_name": "Test Buyer",
                "email": EMAIL,
                "mobile_number": "555-0101",
                "password": PASSWORD,
                "confirm_password": PASSWORD,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("mobile_number", response.data["errors"])

    def test_failed_otp_attempts_are_persisted_and_limited(self):
        user, _ = self.create_verified_customer()
        codes = {}
        with patch(
            "api.account_services.deliver_otp",
            side_effect=lambda channel, recipient, code, purpose: codes.update(
                {channel: code}
            ),
        ):
            challenge = issue_challenge(
                user,
                OTPChallenge.Channel.EMAIL,
                OTPChallenge.Purpose.PASSWORD_RESET,
            )
        for _ in range(5):
            with self.assertRaises(OTPError):
                verify_challenge(
                    challenge.pk,
                    "000000" if codes["email"] != "000000" else "000001",
                    OTPChallenge.Purpose.PASSWORD_RESET,
                )
        challenge.refresh_from_db()
        self.assertEqual(challenge.attempts, 5)
        with self.assertRaises(OTPError):
            verify_challenge(
                challenge.pk,
                codes["email"],
                OTPChallenge.Purpose.PASSWORD_RESET,
            )

    def test_expired_otp_is_rejected(self):
        user, _ = self.create_verified_customer()
        with patch("api.account_services.deliver_otp"):
            challenge = issue_challenge(
                user,
                OTPChallenge.Channel.EMAIL,
                OTPChallenge.Purpose.PASSWORD_RESET,
            )
        OTPChallenge.objects.filter(pk=challenge.pk).update(
            expires_at=timezone.now() - timedelta(minutes=1)
        )
        with self.assertRaises(OTPError):
            verify_challenge(
                challenge.pk,
                "000000",
                OTPChallenge.Purpose.PASSWORD_RESET,
            )

    def test_customer_can_login_by_verified_email_but_not_unverified_mobile(self):
        registration, codes = self.register_customer()
        self.verify_customer(registration, codes)
        response = self.post_json(
            "auth-login",
            {"identity": EMAIL, "password": PASSWORD},
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["user"]["role"], "customer")
        self.assertFalse(response.data["user"]["mobile_verified"])
        self.csrf_token = response.data["csrf_token"]
        mobile_login = self.post_json(
            "auth-login",
            {"identity": MOBILE, "password": PASSWORD},
        )
        self.assertEqual(mobile_login.status_code, 401)

    def test_unverified_customer_cannot_login(self):
        self.register_customer()
        response = self.post_json(
            "auth-login",
            {"identity": EMAIL, "password": PASSWORD},
        )
        self.assertEqual(response.status_code, 401)

    def test_customer_session_cannot_access_operations(self):
        user, _ = self.create_verified_customer()
        self.client.force_authenticate(user=user)
        response = self.client.get(reverse("operations-farm-list"))
        self.assertEqual(response.status_code, 403)

    def test_staff_login_requires_staff_account_and_permissions_stay_backend_enforced(self):
        user_model = get_user_model()
        staff = user_model.objects.create_user(
            username="operations-staff",
            email="staff@example.com",
            password=PASSWORD,
            is_staff=True,
        )
        view_farm = Permission.objects.get(
            content_type__app_label="api",
            codename="view_farm",
        )
        staff.user_permissions.add(view_farm)
        response = self.post_json(
            "auth-operations-login",
            {"identity": "staff@example.com", "password": PASSWORD},
        )
        self.assertEqual(response.status_code, 200, response.data)
        self.assertEqual(response.data["user"]["role"], "staff")
        self.csrf_token = response.data["csrf_token"]
        self.assertEqual(
            self.client.get(reverse("operations-farm-list")).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(reverse("operations-harvest-list")).status_code,
            403,
        )
        self.assertFalse(staff.is_superuser)

    def test_staff_change_permission_is_required_for_record_updates(self):
        user_model = get_user_model()
        staff = user_model.objects.create_user(
            username="operations-editor",
            email="editor@example.com",
            password=PASSWORD,
            is_staff=True,
        )
        farm = Farm.objects.create(reference="FARM-EDIT", name="Farm record", location="Unknown")
        view_farm = Permission.objects.get(
            content_type__app_label="api",
            codename="view_farm",
        )
        change_farm = Permission.objects.get(
            content_type__app_label="api",
            codename="change_farm",
        )
        staff.user_permissions.add(view_farm)
        self.client.force_authenticate(user=staff)
        url = reverse("operations-farm-detail", kwargs={"reference": farm.reference})
        denied = self.client.patch(url, {"name": "Updated farm"}, format="json")
        self.assertEqual(denied.status_code, 403)
        staff.user_permissions.add(change_farm)
        staff = user_model.objects.get(pk=staff.pk)
        self.client.force_authenticate(user=staff)
        updated = self.client.patch(url, {"name": "Updated farm"}, format="json")
        self.assertEqual(updated.status_code, 200, updated.data)
        farm.refresh_from_db()
        self.assertEqual(farm.name, "Updated farm")

    def test_password_recovery_is_generic_and_resets_password_after_otp(self):
        user, _ = self.create_verified_customer()
        codes = {}
        with patch(
            "api.account_services.deliver_otp",
            side_effect=lambda channel, recipient, code, purpose: codes.update(
                {channel: code}
            ),
        ):
            start = self.post_json(
                "auth-recovery-start",
                {"identity": EMAIL, "channel": "email"},
            )
        self.assertEqual(start.status_code, 202)
        self.assertNotIn("code", start.data)
        verify = self.post_json(
            "auth-recovery-verify",
            {"challenge_id": start.data["flow_id"], "code": codes["email"]},
        )
        self.assertEqual(verify.status_code, 200, verify.data)
        reset = self.post_json(
            "auth-recovery-reset",
            {
                "flow_id": start.data["flow_id"],
                "password": "New!SecureOwnerPass1988",
                "confirm_password": "New!SecureOwnerPass1988",
            },
        )
        self.assertEqual(reset.status_code, 200, reset.data)
        user.refresh_from_db()
        self.assertTrue(user.check_password("New!SecureOwnerPass1988"))
        self.assertEqual(
            self.post_json(
                "auth-recovery-reset",
                {
                    "flow_id": start.data["flow_id"],
                    "password": PASSWORD,
                    "confirm_password": PASSWORD,
                },
            ).status_code,
            400,
        )

    def test_sms_password_recovery_is_unavailable_without_attempting_delivery(self):
        self.create_verified_customer()
        with patch("api.account_services.deliver_otp") as delivery:
            response = self.post_json(
                "auth-recovery-start",
                {"identity": MOBILE, "channel": "sms"},
            )
        self.assertEqual(response.status_code, 400)
        delivery.assert_not_called()

    def test_password_reset_invalidates_another_active_session(self):
        self.create_verified_customer()
        other_client = APIClient(enforce_csrf_checks=True)
        csrf = other_client.get(reverse("auth-csrf")).data["csrf_token"]
        login = other_client.post(
            reverse("auth-login"),
            {"identity": EMAIL, "password": PASSWORD},
            format="json",
            HTTP_X_CSRFTOKEN=csrf,
        )
        self.assertEqual(login.status_code, 200)
        codes = {}
        with patch(
            "api.account_services.deliver_otp",
            side_effect=lambda channel, recipient, code, purpose: codes.update(
                {channel: code}
            ),
        ):
            start = self.post_json(
                "auth-recovery-start",
                {"identity": EMAIL, "channel": "email"},
            )
        self.post_json(
            "auth-recovery-verify",
            {"challenge_id": start.data["flow_id"], "code": codes["email"]},
        )
        reset = self.post_json(
            "auth-recovery-reset",
            {
                "flow_id": start.data["flow_id"],
                "password": "Another!SecurePass1989",
                "confirm_password": "Another!SecurePass1989",
            },
        )
        self.assertEqual(reset.status_code, 200, reset.data)
        self.assertEqual(
            other_client.get(reverse("auth-me")).data["user"],
            None,
        )

    def test_registration_resend_cooldown_is_enforced(self):
        registration, _ = self.register_customer()
        response = self.post_json(
            "auth-resend-otp",
            {"challenge_id": registration.data["challenge_id"]},
        )
        self.assertEqual(response.status_code, 429)

    @override_settings(
        EMAIL_PROVIDER="gmail",
        EMAIL_HOST="smtp.gmail.com",
        EMAIL_PORT=587,
        EMAIL_USE_TLS=True,
        EMAIL_USE_SSL=False,
        EMAIL_HOST_USER="",
        EMAIL_HOST_PASSWORD="",
        DEFAULT_FROM_EMAIL="",
    )
    def test_missing_gmail_credentials_fail_safely_without_creating_account(self):
        response = self.post_json(
            "auth-register",
            {
                "full_name": "Test Buyer",
                "email": EMAIL,
                "mobile_number": MOBILE,
                "password": PASSWORD,
                "confirm_password": PASSWORD,
            },
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            set(response.data),
            {"challenge_id", "email_verified", "mobile_verified", "message"},
        )
        self.assertNotIn("code", response.data)
        self.assertFalse(get_user_model().objects.filter(email=EMAIL).exists())
        self.assertFalse(OTPChallenge.objects.exists())

    def test_email_delivery_failure_does_not_activate_or_leave_partial_account(self):
        with patch(
            "api.account_services.deliver_otp",
            side_effect=DeliveryUnavailable("safe provider failure"),
        ) as delivery:
            response = self.post_json(
                "auth-register",
                {
                    "full_name": "Test Buyer",
                    "email": EMAIL,
                    "mobile_number": MOBILE,
                    "password": PASSWORD,
                    "confirm_password": PASSWORD,
                },
            )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            set(response.data),
            {"challenge_id", "email_verified", "mobile_verified", "message"},
        )
        self.assertEqual(delivery.call_count, 1)
        self.assertEqual(delivery.call_args.args[0], OTPChallenge.Channel.EMAIL)
        self.assertFalse(get_user_model().objects.filter(email=EMAIL).exists())
        self.assertFalse(OTPChallenge.objects.exists())

    @override_settings(
        EMAIL_PROVIDER="gmail",
        EMAIL_HOST="smtp.gmail.com",
        EMAIL_PORT=587,
        EMAIL_USE_TLS=True,
        EMAIL_USE_SSL=False,
        EMAIL_HOST_USER="sender@gmail.com",
        EMAIL_HOST_PASSWORD="app-password",
        DEFAULT_FROM_EMAIL="sender@gmail.com",
    )
    def test_smtp_failure_is_safe_and_does_not_expose_otp(self):
        with patch.object(
            EmailMessage,
            "send",
            side_effect=smtplib.SMTPAuthenticationError(535, b"authentication failed"),
        ):
            with self.assertRaises(DeliveryUnavailable) as error:
                deliver_otp("email", EMAIL, "123456", "registration")
        self.assertNotIn("123456", str(error.exception))

    def test_sms_delivery_is_disabled_and_never_calls_a_provider(self):
        with patch.object(EmailMessage, "send") as email_send:
            with self.assertRaises(DeliveryUnavailable):
                deliver_otp("sms", MOBILE, "123456", "registration")
        email_send.assert_not_called()
        self.assertFalse(provider_configured("sms"))

    @override_settings(
        EMAIL_PROVIDER="gmail",
        EMAIL_HOST="smtp.gmail.com",
        EMAIL_PORT=587,
        EMAIL_USE_TLS=True,
        EMAIL_USE_SSL=False,
        EMAIL_HOST_USER="sender@gmail.com",
        EMAIL_HOST_PASSWORD="app-password",
        DEFAULT_FROM_EMAIL="sender@gmail.com",
    )
    def test_only_the_approved_gmail_smtp_configuration_is_accepted(self):
        self.assertTrue(provider_configured("email"))

    @override_settings(
        EMAIL_PROVIDER="another-provider",
        EMAIL_HOST="smtp.example.net",
        EMAIL_PORT=587,
        EMAIL_USE_TLS=True,
        EMAIL_USE_SSL=False,
        EMAIL_HOST_USER="smtp-login",
        EMAIL_HOST_PASSWORD="smtp-key",
        DEFAULT_FROM_EMAIL="verified@example.com",
    )
    def test_alternate_provider_cannot_be_used_as_fallback(self):
        self.assertFalse(provider_configured("email"))
        with self.assertRaises(DeliveryUnavailable):
            deliver_otp("email", EMAIL, "123456", "registration")

    def test_recovery_start_does_not_disclose_account_existence(self):
        known = self.post_json(
            "auth-recovery-start",
            {"identity": EMAIL, "channel": "email"},
        )
        unknown = self.post_json(
            "auth-recovery-start",
            {"identity": "missing@example.com", "channel": "email"},
        )
        self.assertEqual(known.status_code, unknown.status_code)
        self.assertEqual(known.data["message"], unknown.data["message"])
        self.assertNotEqual(known.data["flow_id"], unknown.data["flow_id"])

    @override_settings(
        EMAIL_PROVIDER="",
        EMAIL_HOST="",
        EMAIL_PORT=587,
        EMAIL_USE_TLS=True,
        EMAIL_USE_SSL=False,
        EMAIL_HOST_USER="",
        EMAIL_HOST_PASSWORD="",
        DEFAULT_FROM_EMAIL="",
    )
    def test_provider_configuration_is_not_faked_and_health_is_admin_only(self):
        self.assertFalse(provider_configured("email"))
        self.assertFalse(provider_configured("sms"))
        response = self.client.get(reverse("auth-provider-health"))
        self.assertEqual(response.status_code, 403)
