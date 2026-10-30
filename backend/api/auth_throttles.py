import hashlib
import uuid

from rest_framework.throttling import SimpleRateThrottle

from .models import AccountProfile, OTPChallenge


class AccountThrottle(SimpleRateThrottle):
    scope = "auth_account"

    def get_cache_key(self, request, view):
        data = request.data if hasattr(request, "data") else {}
        if not isinstance(data, dict):
            data = {}
        identity = str(data.get("identity", "")).strip().lower()
        challenge_value = data.get("challenge_id") or data.get("flow_id")
        account_id = None
        if challenge_value:
            try:
                challenge_id = uuid.UUID(str(challenge_value))
            except (TypeError, ValueError):
                challenge_id = None
            if challenge_id:
                account_id = OTPChallenge.objects.filter(
                    pk=challenge_id
                ).values_list("user_id", flat=True).first()
        if account_id is None and identity:
            profile = AccountProfile.objects.filter(
                email_key__iexact=identity
            ).only("user_id").first()
            if profile:
                account_id = profile.user_id
            else:
                mobile_profile = AccountProfile.objects.filter(
                    mobile_number=identity
                ).only("user_id").first()
                if mobile_profile:
                    account_id = mobile_profile.user_id

        if account_id is not None:
            subject = f"user:{account_id}"
        else:
            candidate = identity or str(data.get("email", "")).strip().lower()
            if not candidate:
                candidate = str(data.get("mobile_number", "")).strip()
            if not candidate:
                return None
            subject = f"identity:{candidate}"

        hashed_subject = hashlib.sha256(subject.encode("utf-8")).hexdigest()
        return self.cache_format % {
            "scope": self.scope,
            "ident": hashed_subject,
        }
