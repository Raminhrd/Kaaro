import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken

from services.models import Service
from tasks.models import Task
from specialists.models import SpecialistRequest

User = get_user_model()
pytestmark = pytest.mark.django_db


def auth_client(api_client, user):
    refresh = RefreshToken.for_user(user)
    api_client.cookies["accessToken"] = str(refresh.access_token)
    return api_client


def make_user(phone, role=None):
    u = User.objects.create_user(phone_number=phone, password="x12345678")
    if role is not None:
        u.role = role
        u.save(update_fields=["role"])
    return u


def approve_specialist(user):
    sr, _ = SpecialistRequest.objects.get_or_create(user=user)
    sr.status = SpecialistRequest.Status.APPROVED
    sr.save(update_fields=["status"])
    return sr


def make_service():

    return Service.objects.create(
        title="Cleaning",
        service_type=Service.Type.CLEANING,
        is_active=True,
        base_duration_minutes=60,
    )


def extract_items(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and "results" in payload and isinstance(payload["results"], list):
        return payload["results"]
    raise AssertionError(f"Unexpected response shape: {payload}")


class TestTaskEndpoints:
    def test_customer_can_create_task(self, api_client):
        customer = make_user("+989121111111", role=User.RoleChoices.CUSTOMER)
        service = make_service()

        client = auth_client(api_client, customer)
        payload = {
            "service": service.id,
            "contact_name": "Ramin",
            "contact_phone": "09120000000",
            "address": "Tehran, Valiasr",
            "note": "please come ASAP",
        }

        res = client.post(reverse("task-list"), data=payload, format="json")
        assert res.status_code == 201

        body = res.json()
        assert body["service"] == service.id
        assert body["status"] == Task.Status.PENDING
        assert body["specialist"] is None

        task = Task.objects.get(id=body["id"])
        assert task.customer_id == customer.id

    def test_customer_list_returns_only_own_tasks(self, api_client):
        service = make_service()
        c1 = make_user("+989121111111", role=User.RoleChoices.CUSTOMER)
        c2 = make_user("+989122222222", role=User.RoleChoices.CUSTOMER)

        t1 = Task.objects.create(
            customer=c1,
            service=service,
            contact_name="A",
            contact_phone="09120000001",
            address="Addr1",
        )
        Task.objects.create(
            customer=c2,
            service=service,
            contact_name="B",
            contact_phone="09120000002",
            address="Addr2",
        )

        client = auth_client(api_client, c1)
        res = client.get(reverse("task-list"))
        assert res.status_code == 200

        items = extract_items(res.json())
        assert len(items) == 1
        assert items[0]["id"] == t1.id

    def test_available_requires_approved_specialist(self, api_client):
        service = make_service()
        customer = make_user("+989121111111", role=User.RoleChoices.CUSTOMER)
        Task.objects.create(
            customer=customer,
            service=service,
            contact_name="A",
            contact_phone="09120000001",
            address="Addr1",
        )

        specialist = make_user("+989123333333", role=User.RoleChoices.SPECIALIST)
        client = auth_client(api_client, specialist)

        # not approved => 403
        res = client.get(reverse("task-available"))
        assert res.status_code == 403

        # approved => 200
        approve_specialist(specialist)
        res2 = client.get(reverse("task-available"))
        assert res2.status_code == 200

        items = extract_items(res2.json())
        assert len(items) == 1

    def test_specialist_can_accept_task_and_task_is_locked(self, api_client):
        service = make_service()
        customer = make_user("+989121111111", role=User.RoleChoices.CUSTOMER)

        task = Task.objects.create(
            customer=customer,
            service=service,
            contact_name="A",
            contact_phone="09120000001",
            address="Addr1",
        )

        s1 = make_user("+989123333333", role=User.RoleChoices.SPECIALIST)
        s2 = make_user("+989124444444", role=User.RoleChoices.SPECIALIST)
        approve_specialist(s1)
        approve_specialist(s2)

        c1 = auth_client(api_client, s1)
        c2 = auth_client(api_client, s2)

        # accepts successfully
        res1 = c1.post(reverse("task-accept", kwargs={"pk": task.id}), data={}, format="json")
        assert res1.status_code == 200
        body1 = res1.json()

        assert body1["status"] == Task.Status.ACCEPTED
        assert body1["specialist"] == s1.id

        # cannot accept anymore (locked)
        res2 = c2.post(reverse("task-accept", kwargs={"pk": task.id}), data={}, format="json")
        assert res2.status_code == 400

        task.refresh_from_db()
        assert task.specialist_id == s1.id
        assert task.status == Task.Status.ACCEPTED

    def test_available_does_not_show_accepted_tasks(self, api_client):
        service = make_service()
        customer = make_user("+989121111111", role=User.RoleChoices.CUSTOMER)

        task = Task.objects.create(
            customer=customer,
            service=service,
            contact_name="A",
            contact_phone="09120000001",
            address="Addr1",
        )

        specialist = make_user("+989123333333", role=User.RoleChoices.SPECIALIST)
        approve_specialist(specialist)

        client = auth_client(api_client, specialist)

        # before accept => visible
        res = client.get(reverse("task-available"))
        assert res.status_code == 200
        items = extract_items(res.json())
        assert any(i["id"] == task.id for i in items)

        # accept
        client.post(reverse("task-accept", kwargs={"pk": task.id}), data={}, format="json")

        # after accept => not visible
        res2 = client.get(reverse("task-available"))
        assert res2.status_code == 200
        items2 = extract_items(res2.json())
        assert all(i["id"] != task.id for i in items2)

    def test_specialist_can_start_and_done_task(self, api_client):
        service = make_service()
        customer = make_user("+989121111111", role=User.RoleChoices.CUSTOMER)

        task = Task.objects.create(
            customer=customer,
            service=service,
            contact_name="A",
            contact_phone="09120000001",
            address="Addr1",
        )

        specialist = make_user("+989123333333", role=User.RoleChoices.SPECIALIST)
        approve_specialist(specialist)
        client = auth_client(api_client, specialist)

        # accept -> ACCEPTED
        res_accept = client.post(reverse("task-accept", kwargs={"pk": task.id}), data={}, format="json")
        assert res_accept.status_code == 200
        assert res_accept.json()["status"] == Task.Status.ACCEPTED

        # start -> IN_PROGRESS
        res_start = client.post(reverse("task-start", kwargs={"pk": task.id}), data={}, format="json")
        assert res_start.status_code == 200
        assert res_start.json()["status"] == Task.Status.IN_PROGRESS

        # done -> DONE
        res_done = client.post(reverse("task-done", kwargs={"pk": task.id}), data={}, format="json")
        assert res_done.status_code == 200
        assert res_done.json()["status"] == Task.Status.DONE

    def test_specialist_cannot_done_without_start(self, api_client):
        service = make_service()
        customer = make_user("+989121111111", role=User.RoleChoices.CUSTOMER)

        specialist = make_user("+989123333333", role=User.RoleChoices.SPECIALIST)
        approve_specialist(specialist)

        task = Task.objects.create(
            customer=customer,
            service=service,
            specialist=specialist,
            contact_name="A",
            contact_phone="09120000001",
            address="Addr1",
            status=Task.Status.ACCEPTED,
        )

        client = auth_client(api_client, specialist)
        res = client.post(reverse("task-done", kwargs={"pk": task.id}), data={}, format="json")
        assert res.status_code == 400

    def test_specialist_cannot_start_someone_elses_task(self, api_client):
        service = make_service()
        customer = make_user("+989121111111", role=User.RoleChoices.CUSTOMER)

        owner = make_user("+989123333333", role=User.RoleChoices.SPECIALIST)
        other = make_user("+989124444444", role=User.RoleChoices.SPECIALIST)
        approve_specialist(owner)
        approve_specialist(other)

        task = Task.objects.create(
            customer=customer,
            service=service,
            specialist=owner,
            contact_name="A",
            contact_phone="09120000001",
            address="Addr1",
            status=Task.Status.ACCEPTED,
        )

        client_other = auth_client(api_client, other)
        res = client_other.post(reverse("task-start", kwargs={"pk": task.id}), data={}, format="json")
        assert res.status_code == 403

    def test_customer_can_cancel_own_task(self, api_client):
        service = make_service()
        customer = make_user("+989121111111", role=User.RoleChoices.CUSTOMER)

        task = Task.objects.create(
            customer=customer,
            service=service,
            contact_name="A",
            contact_phone="09120000001",
            address="Addr1",
            status=Task.Status.PENDING,
        )

        client = auth_client(api_client, customer)
        res = client.post(reverse("task-cancel", kwargs={"pk": task.id}), data={}, format="json")
        assert res.status_code == 200

        task.refresh_from_db()
        assert task.status == Task.Status.CANCELED

    def test_customer_cannot_cancel_others_task(self, api_client):
        service = make_service()
        c1 = make_user("+989121111111", role=User.RoleChoices.CUSTOMER)
        c2 = make_user("+989122222222", role=User.RoleChoices.CUSTOMER)

        task = Task.objects.create(
            customer=c1,
            service=service,
            contact_name="A",
            contact_phone="09120000001",
            address="Addr1",
            status=Task.Status.PENDING,
        )

        client = auth_client(api_client, c2)
        res = client.post(reverse("task-cancel", kwargs={"pk": task.id}), data={}, format="json")
        assert res.status_code == 403
