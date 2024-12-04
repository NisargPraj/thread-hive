import jwt
from rest_framework.permissions import BasePermission
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


class IsAuthenticatedCustom(BasePermission):
    """
    Custom permission to validate JWT authentication without triggering Django's ORM.
    """

    def has_permission(self, request, view):
        # Extract the token from the Authorization header
        auth_header = request.headers.get('Authorization', '')
        if not auth_header or not auth_header.startswith('Bearer '):
            return False  # No token or invalid format

        token = auth_header.split(' ')[1]
        try:
            # Decode the token using the same secret and algorithm
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            request.user = payload.get('username')  # Attach username to the request
            if not request.user:
                raise AuthenticationFailed("Invalid token: username not found.")
            return True
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired.")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token.")
