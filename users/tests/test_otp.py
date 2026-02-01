import pytest

from django.core.cache import cache
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.tokens import RefreshToken

from users.utils import normalize_phone_number
from users import defaults

User = get_user_model()
pytestmark = pytest.mark.django_db


class TestOTPAuth:
    def test_otp_request_stores_otp_and_calls_celery(self, api_client, monkeypatch):
        raw_phone = "+989121234567"
        normalized_phone = normalize_phone_number(raw_phone)
        fixed_otp = "1234"

        # Mock OTP generator
        monkeypatch.setattr("users.views.generate_otp", lambda length=4: fixed_otp)

        # Mock celery delay
        called = {"ok": False, "args": None}

        def fake_delay(p, o):
            called["ok"] = True
            called["args"] = (p, o)

        monkeypatch.setattr("users.views.send_otp_sms.delay", fake_delay)

        res = api_client.post(
            "/users/otp/request/",
            data={"phone_number": raw_phone},
            format="json",
        )

        assert res.status_code == 200
        assert cache.get(f"otp_{normalized_phone}") == fixed_otp
        assert called["ok"] is True
        assert called["args"] == (normalized_phone, fixed_otp)

    def test_otp_login_sets_cookies_and_deletes_cache(self, api_client):
        raw_phone = "+989121234567"
        normalized_phone = normalize_phone_number(raw_phone)
        otp = "1234"

        User.objects.create_user(phone_number=normalized_phone, password="x12345678")
        cache.set(f"otp_{normalized_phone}", otp, timeout=120)

        res = api_client.post(
            "/users/otp/login/",
            data={"phone_number": raw_phone, "otp": otp},
            format="json",
        )

        assert res.status_code == 200

        assert cache.get(f"otp_{normalized_phone}") is None

        data = res.json()
        assert "access" in data
        assert "refresh" in data

        cookies = res.cookies
        assert defaults.ACCESS_TOKEN_COOKIE_KEY_NAME in cookies
        assert defaults.REFRESH_TOKEN_COOKIE_KEY_NAME in cookies


class TestUserInfo:
    def test_user_info_returns_data(self, api_client):
        raw_phone = "+989121234567"
        normalized_phone = normalize_phone_number(raw_phone)

        user = User.objects.create_user(phone_number=normalized_phone, password="x12345678")

        user.status = User.StatusChoices.ACTIVE
        user.save(update_fields=["status"])

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)

        api_client.cookies[defaults.ACCESS_TOKEN_COOKIE_KEY_NAME] = access

        res = api_client.get("/users/info/")

        assert res.status_code == 200

        assert res.json()["phone_number"] == str(user.phone_number)
