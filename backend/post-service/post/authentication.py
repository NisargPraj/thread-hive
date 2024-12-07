from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Override to handle custom user validation logic.
        """
        username = validated_token.get('username')  # Matches USER_ID_CLAIM
        if not username:
            raise AuthenticationFailed('Token contained no recognizable user identification')
        return username
