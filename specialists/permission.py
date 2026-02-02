from users.models import User
from rest_framework.permissions import BasePermission
from specialists.models import SpecialistRequest

class IsApprovedSpecialist(BasePermission):
    message = "Your specialist account is not approved yet."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if getattr(user, "role", None) != User.RoleChoices.SPECIALIST:
            return False

        sr = getattr(user, "specialist_request", None)
        return bool(sr and sr.status == SpecialistRequest.Status.APPROVED)