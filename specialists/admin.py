from django.contrib import admin
from django.utils import timezone

from specialists.models import SpecialistRequest, SpecialistProfile
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(SpecialistRequest)
class SpecialistRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "status",
        "created_at",
        "reviewed_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("user__phone_number", "user__first_name", "user__last_name")
    autocomplete_fields = ("user",)
    actions = ("approve_requests", "reject_requests")

    @admin.action(description="Approve selected specialist requests")
    def approve_requests(self, request, queryset):
        now = timezone.now()

        pending = queryset.filter(status=SpecialistRequest.Status.PENDING).select_related("user")

        for sr in pending:
            sr.status = SpecialistRequest.Status.APPROVED
            sr.reviewed_at = now
            sr.save(update_fields=["status", "reviewed_at"])

            user = sr.user
            user.role = User.RoleChoices.SPECIALIST
            user.save(update_fields=["role"])

            SpecialistProfile.objects.get_or_create(user=user)


@admin.register(SpecialistProfile)
class SpecialistProfileAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "national_code",
        "city",
        "is_verified",
        "created_at",
    )
    list_filter = ("is_verified", "created_at", "city")
    search_fields = ("user__phone_number", "national_code", "city")
    autocomplete_fields = ("user",)