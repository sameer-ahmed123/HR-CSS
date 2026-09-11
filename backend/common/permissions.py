from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    def __init__(self, allowed_roles=None):
        self.allowed_roles = set(allowed_roles or [])

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in self.allowed_roles
        )

    def __call__(self):
        return self
