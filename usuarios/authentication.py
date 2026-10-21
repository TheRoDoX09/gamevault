# Autenticación con SimpleJWT, pero el token viaja en una cookie httpOnly
# en lugar del header Authorization (JavaScript no puede leerla: protege contra XSS).
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken


class CookieJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        token = request.COOKIES.get(settings.JWT_COOKIE['key'])
        if not token:
            return None
        try:
            validado = self.get_validated_token(token)
            return self.get_user(validado), validado
        except (InvalidToken, TokenError, AuthenticationFailed):
            # Token vencido, alterado o de un usuario eliminado: se trata como visitante anónimo
            return None


def crear_sesion(response, user):
    response.set_cookie(value=str(AccessToken.for_user(user)), **settings.JWT_COOKIE)


def cerrar_sesion(response):
    response.delete_cookie(settings.JWT_COOKIE['key'], samesite=settings.JWT_COOKIE['samesite'])
