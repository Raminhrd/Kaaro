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


class TestSpecialistRequestMe:
    def test_create_request(self, api_client):
        user = User.objects.create_user(phone_number="+989121111111", password="x12345678")
        client = auth_client(api_client, user)

        res = client.post(reverse("specialist-request-me"), data={"note": "I have experience"}, format="json")
        assert res.status_code == 201
        assert res.json()["status"] == SpecialistRequest.Status.PENDING

    def test_get_request_404_if_missing(self, api_client):
        user = User.objects.create_user(phone_number="+989121111111", password="x12345678")
        client = auth_client(api_client, user)

        res = client.get(reverse("specialist-request-me"))
        assert res.status_code == 404

    def test_get_request_ok(self, api_client):
        user = User.objects.create_user(phone_number="+989121111111", password="x12345678")
        SpecialistRequest.objects.create(user=user, note="hi")

        client = auth_client(api_client, user)
        res = client.get(reverse("specialist-request-me"))
        assert res.status_code == 200
        assert res.json()["note"] == "hi"
