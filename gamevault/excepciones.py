# Manejador de errores de DRF: todas las respuestas de error usan {"error": "..."},
# el formato que espera el frontend (public/js/common.js).
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated, Throttled
from rest_framework.views import exception_handler

from .throttling import LimiteAuth


def manejador_errores(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return None

    if isinstance(exc, (NotAuthenticated, AuthenticationFailed)):
        response.data = {'error': 'Debes iniciar sesión.'}
    elif isinstance(exc, Throttled):
        vista = context.get('view')
        if vista and any(isinstance(t, LimiteAuth) for t in vista.get_throttles()):
            response.data = {'error': 'Demasiados intentos. Espera 15 minutos e inténtalo de nuevo.'}
        else:
            response.data = {'error': 'Demasiadas peticiones. Espera un momento e inténtalo de nuevo.'}
    elif isinstance(response.data, dict) and 'detail' in response.data:
        response.data = {'error': str(response.data['detail'])}
    return response
