from rest_framework.permissions import BasePermission


class IsAuthenticatedCustom(BasePermission):
    """
    Custom permission to validate token presence.
    The actual validation is done by the user service.
    """

    def has_permission(self, request, view):
        # If authentication was successful, request.user will be the token
        return bool(request.user and request.user != "")
