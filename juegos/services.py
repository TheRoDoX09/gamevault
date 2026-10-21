# juegos/services.py
# Capa de servicios: consumo de la API externa de RAWG separado de las vistas.
import requests
from django.conf import settings
from rest_framework.exceptions import APIException

RAWG_BASE = 'https://api.rawg.io/api'


class ErrorRAWG(APIException):
    status_code = 502
    default_detail = 'Error al consultar la API de RAWG.'

    def __init__(self, detail=None, status_code=502):
        super().__init__(detail)
        self.status_code = status_code


# Adapter: traduce el JSON de RAWG al formato (en español) que usa nuestro frontend.
def adaptar_resumen(j):
    return {
        'id': j['id'],
        'nombre': j['name'],
        'imagen': j.get('background_image'),
        'lanzamiento': j.get('released'),
        'rating': j.get('rating'),
        'metacritic': j.get('metacritic'),
        'generos': [g['name'] for g in j.get('genres') or []],
        'plataformas': [p['platform']['name'] for p in j.get('parent_platforms') or []],
    }


def adaptar_detalle(j, capturas):
    return {
        'id': j['id'],
        'nombre': j['name'],
        'descripcion': j.get('description_raw'),
        'imagen': j.get('background_image'),
        'lanzamiento': j.get('released'),
        'rating': j.get('rating'),
        'metacritic': j.get('metacritic'),
        'tiempo': j.get('playtime'),
        'sitio': j.get('website'),
        'generos': [g['name'] for g in j.get('genres') or []],
        'plataformas': [p['platform']['name'] for p in j.get('platforms') or []],
        'desarrolladores': [d['name'] for d in j.get('developers') or []],
        'capturas': [c['image'] for c in capturas[:6]],
    }


# Facade: las vistas solo llaman buscar_juegos / detalle_juego / generos.
# Aquí se ocultan la URL de RAWG, la clave del .env, el timeout y el manejo de errores.
# El navegador nunca ve la clave.
class ClienteRAWG:
    def _get(self, ruta, params=None):
        clave = settings.RAWG_API_KEY
        if not clave or clave == 'tu_clave_de_rawg_aqui':
            raise ErrorRAWG('La clave de la API de RAWG no está configurada en el archivo .env.', 503)
        params = {k: v for k, v in (params or {}).items() if v not in (None, '')}
        params['key'] = clave
        try:
            resp = requests.get(RAWG_BASE + ruta, params=params, timeout=10)
        except requests.RequestException:
            raise ErrorRAWG()
        if resp.status_code == 404:
            raise ErrorRAWG('Juego no encontrado.', 404)
        if not resp.ok:
            raise ErrorRAWG()
        return resp.json()

    def buscar_juegos(self, busqueda, genero, orden, pagina):
        data = self._get('/games', {
            'search': busqueda,
            'genres': genero,
            'ordering': None if busqueda else orden,
            'page': pagina,
            'page_size': 12,
        })
        return {
            'total': data['count'],
            'siguiente': bool(data.get('next')),
            'juegos': [adaptar_resumen(j) for j in data['results']],
        }

    def detalle_juego(self, juego_id):
        juego = self._get(f'/games/{juego_id}')
        try:
            capturas = self._get(f'/games/{juego_id}/screenshots')['results']
        except ErrorRAWG:
            capturas = []
        return adaptar_detalle(juego, capturas)

    def generos(self):
        data = self._get('/genres', {'page_size': 20})
        return [{'slug': g['slug'], 'nombre': g['name']} for g in data['results']]
