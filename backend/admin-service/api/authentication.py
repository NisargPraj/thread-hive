from rest_framework import authentication
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication
import logging

logger = logging.getLogger(__name__)


class CustomTokenAuthentication(JWTAuthentication):
    def authenticate(self, request):
        """
        Authenticate using JWT token and pass it along to the user service.
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        try:
            # Get the raw token
            auth_parts = auth_header.split()
            if len(auth_parts) != 2 or auth_parts[0].lower() != "bearer":
                raise exceptions.AuthenticationFailed("Invalid token format")

            token = auth_parts[1]
            logger.debug(f"Received token: {token}")

            # Return the raw token as both the user and auth
            return (token, token)

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise exceptions.AuthenticationFailed("Authentication failed")
