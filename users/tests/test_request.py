import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import SpecialistRequest

User = get_user_model()
pytestmark = pytest.mark.django_db


def auth_client(api_client, user):
    refresh = RefreshToken.for_user(user)
    api_client.cookies["accessToken"] = str(refresh.access_token)
    return api_client


class TestSpecialistRequestFlow:
    def test_user_can_create_specialist_request(self, api_client):
        user = User.objects.create_user(phone_number="+989121111111", password="x12345678")
        client = auth_client(api_client, user)

        res = client.post(reverse("specialist-request-me"), data={"note": "I have experience"}, format="json")
        assert res.status_code == 201

        body = res.json()
        assert body["status"] == SpecialistRequest.Status.PENDING

        sr = SpecialistRequest.objects.get(user=user)
        assert sr.note == "I have experience"

    def test_admin_can_approve_request_and_user_becomes_specialist(self, api_client):
        user = User.objects.create_user(phone_number="+989121111111", password="x12345678")
        sr = SpecialistRequest.objects.create(user=user)

        admin = User.objects.create_user(phone_number="+989120000000", password="x12345678", is_staff=True)
        client = auth_client(api_client, admin)

        res = client.post(
            reverse("specialist-request-admin-decision", kwargs={"pk": sr.id}),
            data={"decision": "approve"},
            format="json",
        )
        assert res.status_code == 200

        user.refresh_from_db()
        sr.refresh_from_db()

        assert sr.status == SpecialistRequest.Status.APPROVED
        assert user.role == User.RoleChoices.SPECIALIST

    def test_admin_can_reject_request(self, api_client):
        user = User.objects.create_user(phone_number="+989121111111", password="x12345678")
        sr = SpecialistRequest.objects.create(user=user)

        admin = User.objects.create_user(phone_number="+989120000000", password="x12345678", is_staff=True)
        client = auth_client(api_client, admin)

        res = client.post(
            reverse("specialist-request-admin-decision", kwargs={"pk": sr.id}),
            data={"decision": "reject"},
            format="json",
        )
        assert res.status_code == 200

        sr.refresh_from_db()
        assert sr.status == SpecialistRequest.Status.REJECTED

    def test_non_admin_cannot_approve_or_reject(self, api_client):
        user = User.objects.create_user(phone_number="+989121111111", password="x12345678")
        sr = SpecialistRequest.objects.create(user=user)

        non_admin = User.objects.create_user(phone_number="+989122222222", password="x12345678")
        client = auth_client(api_client, non_admin)

        res = client.post(
            reverse("specialist-request-admin-decision", kwargs={"pk": sr.id}),
            data={"decision": "approve"},
            format="json",
        )
        assert res.status_code in (403, 401)
