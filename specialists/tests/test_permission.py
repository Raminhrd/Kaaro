import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from specialists.models import SpecialistRequest

User = get_user_model()
pytestmark = pytest.mark.django_db


def auth_client(api_client, user):
    refresh = RefreshToken.for_user(user)
    api_client.cookies["accessToken"] = str(refresh.access_token)
    return api_client


def make_specialist(phone, approved: bool):
    u = User.objects.create_user(phone_number=phone, password="x12345678")
    u.role = User.RoleChoices.SPECIALIST
    u.save(update_fields=["role"])

    sr = SpecialistRequest.objects.create(user=u)
    if approved:
        sr.status = SpecialistRequest.Status.APPROVED
        sr.save(update_fields=["status"])
    return u


class TestApprovedSpecialistPermission:
    def test_available_requires_approved(self, api_client):
        s_not_approved = make_specialist("+989121111111", approved=False)
        s_approved = make_specialist("+989122222222", approved=True)

        c1 = auth_client(api_client, s_not_approved)
        res1 = c1.get(reverse("task-available"))
        assert res1.status_code == 403

        c2 = auth_client(api_client, s_approved)
        res2 = c2.get(reverse("task-available"))
        assert res2.status_code == 200
