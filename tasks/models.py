from django.conf import settings
from django.db import models
from services.models import Service


class Task(models.Model):
    class Status(models.IntegerChoices):
        PENDING = 1, "Pending"
        ACCEPTED = 2, "Accepted"
        IN_PROGRESS = 3, "In Progress"
        DONE = 4, "Done"
        CANCELED = 5, "Canceled"

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    service = models.ForeignKey(
        Service,
        on_delete=models.PROTECT,
        related_name="tasks",
    )

    specialist = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="accepted_tasks",
    )

    status = models.IntegerField(choices=Status.choices, default=Status.PENDING)

    contact_name = models.CharField(max_length=80)
    contact_phone = models.CharField(max_length=20)
    address = models.TextField()

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    note = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Task#{self.id} - {self.get_status_display()}"
