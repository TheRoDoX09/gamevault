# Rate limiting de DRF. Los límites están en settings.REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'].
from rest_framework.throttling import SimpleRateThrottle

SEGUNDOS = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}


class LimiteConPeriodo(SimpleRateThrottle):
    def parse_rate(self, rate):
        # Además de '60/m' acepta periodos como '20/15m' (20 peticiones cada 15 minutos)
        if rate is None:
            return (None, None)
        num, periodo = rate.split('/')
        cantidad = int(periodo[:-1] or 1)
        return (int(num), cantidad * SEGUNDOS[periodo[-1]])

    def get_cache_key(self, request, view):
        # Por usuario si inició sesión, si no por IP
        ident = request.user.pk if request.user and request.user.is_authenticated else self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}


class LimiteAuth(LimiteConPeriodo):
    # Login y registro: contra fuerza bruta
    scope = 'auth'


class LimiteRAWG(LimiteConPeriodo):
    # Proxy hacia la API externa
    scope = 'rawg'
