from django.db import transaction
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from specialists.permission import IsApprovedSpecialist
from tasks.models import Task
from tasks.serializers import TaskCreateSerializer, TaskSerializer
from tasks.utils.views import PaginatedQuerySetMixin
from tasks.filters import TaskFilter


class TaskViewSet(CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet, PaginatedQuerySetMixin):
    permission_classes = [IsAuthenticated]
    filterset_class = TaskFilter
    search_fields = ("contact_name", "contact_phone", "address")
    ordering_fields = ("created_at", "status")
    ordering = ("-created_at",)

    def get_serializer_class(self):
        return TaskCreateSerializer if self.action == "create" else TaskSerializer

    def get_queryset(self):
        user = self.request.user

        base = (
            Task.objects
            .select_related("service", "customer", "specialist")
            .only(
                "id",
                "service__id", "service__title",
                "customer__id", "customer__first_name", "customer__last_name",
                "specialist__id", "specialist__first_name", "specialist__last_name",
                "status",
                "contact_name", "contact_phone", "address",
                "latitude", "longitude",
                "note",
                "created_at",
            )
        )

        if user.role == user.RoleChoices.CUSTOMER:
            return base.filter(customer=user).order_by("-created_at")

        if user.role == user.RoleChoices.SPECIALIST:
            return base.filter(specialist=user).order_by("-created_at")

        return Task.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()
        return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=["get"],
        url_path="available",
        permission_classes=[IsApprovedSpecialist],
    )
    def available(self, request):
        qs = (
            Task.objects
            .select_related("service")
            .only(
                "id",
                "service__id", "service__title",
                "status",
                "contact_name",
                "address",
                "latitude", "longitude",
                "created_at",
            )
            .filter(status=Task.Status.PENDING, specialist__isnull=True)
            .order_by("-created_at")
        )
        qs = self.filter_queryset(qs)
        return self.paginate_and_respond(qs)

    @action(
        detail=True,
        methods=["post"],
        url_path="accept",
        permission_classes=[IsApprovedSpecialist],
    )
    def accept(self, request, pk=None):
        specialist = request.user

        with transaction.atomic():
            task = Task.objects.select_for_update().get(pk=pk)

            if task.status != Task.Status.PENDING or task.specialist_id is not None:
                return Response({"detail": "Task is not available."}, status=status.HTTP_400_BAD_REQUEST)

            task.status = Task.Status.ACCEPTED
            task.specialist = specialist
            task.save(update_fields=["status", "specialist"])

        task.refresh_from_db()
        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path="start",
        permission_classes=[IsApprovedSpecialist],
    )
    def start(self, request, pk=None):
        specialist = request.user

        with transaction.atomic():
            task = Task.objects.select_for_update().get(pk=pk)

            if task.specialist_id != specialist.id:
                return Response({"detail": "You can only start your own accepted task."}, status=status.HTTP_403_FORBIDDEN)

            if task.status != Task.Status.ACCEPTED:
                return Response({"detail": "Task must be in ACCEPTED status to start."}, status=status.HTTP_400_BAD_REQUEST)

            task.status = Task.Status.IN_PROGRESS
            task.save(update_fields=["status"])

        task.refresh_from_db()
        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["post"],
        url_path="done",
        permission_classes=[IsApprovedSpecialist],
    )
    def done(self, request, pk=None):
        specialist = request.user

        with transaction.atomic():
            task = Task.objects.select_for_update().get(pk=pk)

            if task.specialist_id != specialist.id:
                return Response({"detail": "You can only complete your own task."}, status=status.HTTP_403_FORBIDDEN)

            if task.status != Task.Status.IN_PROGRESS:
                return Response({"detail": "Task must be IN_PROGRESS to be completed."}, status=status.HTTP_400_BAD_REQUEST)

            task.status = Task.Status.DONE
            task.save(update_fields=["status"])

        task.refresh_from_db()
        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="cancel", permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        user = request.user
        task = Task.objects.get(pk=pk)

        if task.customer_id != user.id:
            return Response({"detail": "You can only cancel your own task."}, status=status.HTTP_403_FORBIDDEN)

        if task.status not in (Task.Status.PENDING, Task.Status.ACCEPTED):
            return Response({"detail": "Task cannot be canceled now."}, status=status.HTTP_400_BAD_REQUEST)

        task.status = Task.Status.CANCELED
        task.save(update_fields=["status"])

        task.refresh_from_db()
        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)
