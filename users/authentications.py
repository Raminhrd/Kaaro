import logging

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken

from users import defaults

logger = logging.getLogger(__name__)

class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get(defaults.ACCESS_TOKEN_COOKIE_KEY_NAME, None)
        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except (TokenError, InvalidToken):
            return None
