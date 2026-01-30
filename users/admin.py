from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from users.models import User, Role

@admin.register(User)
class UserAdmin(BaseUserAdmin):

    list_display = (
        "id",
        "phone_number",
        "full_name",
        "is_superuser",
    )
    list_filter = (
        "is_active",
        "is_superuser",
        "is_staff",
        "is_phone_verified",
        "gender",
        "date_joined",
        "last_login",
    )
    search_fields = ("phone_number", "first_name", "last_name", "national_identity_number", "email")
    ordering = ("-date_joined",)
    list_per_page = 25
    list_select_related = True

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "gender",
                    "status",
                )
            },
        ),
        ("Permissions", {"fields": ("role",)}),
        ("Verification", {"fields": ("is_phone_verified",)}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "phone_number",
                    "first_name",
                    "last_name",
                    "email",
                    "password1",
                    "password2",
                ),
            },
        ),
    )
    readonly_fields = ("date_joined", "last_login")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name",)