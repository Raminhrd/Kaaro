from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class SpecialistRequest(models.Model):
    class Status(models.IntegerChoices):
        PENDING = 1, "Pending"
        APPROVED = 2, "Approved"
        REJECTED = 3, "Rejected"

    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="specialist_request",)
    status = models.IntegerField(choices=Status.choices, default=Status.PENDING)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user_id} - {self.get_status_display()}"


class SpecialistProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,related_name="specialist_profile",)

    national_code = models.CharField(max_length=10, null=True, blank=True)
    bio = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)

    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"SpecialistProfile({self.user_id})"
