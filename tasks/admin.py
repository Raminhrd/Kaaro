from django.contrib import admin
from tasks.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "service",
        "customer",
        "specialist",
        "status",
        "contact_name",
        "contact_phone",
        "created_at",
    )
    list_filter = ("status", "service", "created_at")
    search_fields = (
        "contact_name",
        "contact_phone",
        "customer__phone_number",
        "specialist__phone_number",
        "address",
    )
    ordering = ("-created_at",)
