from rest_framework.permissions import BasePermission
from users.models import User

class IsApprovedSpecialist(BasePermission):
    message = "Your specialist account is not approved yet."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.role != User.RoleChoices.SPECIALIST:
            return False

        sr = getattr(user, "specialist_request", None)
        return sr is not None and sr.status == sr.Status.APPROVED
