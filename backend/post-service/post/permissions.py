from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed


class IsAuthenticatedCustom(BasePermission):
    """
    Custom permission to validate JWT authentication.
    """

    def has_permission(self, request, view):
        # Check if the request has been authenticated
        if not request.auth:
            return False

        # The auth token is already validated by the authentication class
        return True
